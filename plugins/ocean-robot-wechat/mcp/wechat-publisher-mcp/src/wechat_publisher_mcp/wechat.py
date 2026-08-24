from __future__ import annotations

import asyncio
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

from .config import AccountCredential
from .models import DraftArticle

TOKEN_ERROR_CODES = {40001, 40014, 42001}


class WeChatApiError(RuntimeError):
    def __init__(self, message: str, *, errcode: int | None = None) -> None:
        super().__init__(message)
        self.errcode = errcode


@dataclass(frozen=True)
class TokenEntry:
    value: str
    expires_at: float


class WeChatClient:
    def __init__(
        self,
        accounts: Mapping[str, AccountCredential],
        *,
        base_url: str = "https://api.weixin.qq.com",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.accounts = dict(accounts)
        self.base_url = base_url.rstrip("/")
        self._owns_http_client = http_client is None
        self.http = http_client or httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            transport=httpx.AsyncHTTPTransport(retries=2),
            follow_redirects=False,
        )
        self._tokens: dict[str, TokenEntry] = {}
        self._token_locks: dict[str, asyncio.Lock] = {
            alias: asyncio.Lock() for alias in self.accounts
        }

    async def close(self) -> None:
        if self._owns_http_client:
            await self.http.aclose()

    def account(self, alias: str) -> AccountCredential:
        try:
            return self.accounts[alias]
        except KeyError as exc:
            raise WeChatApiError(f"unknown WeChat account alias: {alias}") from exc

    async def check_account(self, alias: str) -> dict[str, Any]:
        account = self.account(alias)
        await self._access_token(alias)
        entry = self._tokens[alias]
        return {
            "alias": account.alias,
            "name": account.name,
            "account_type": account.account_type,
            "authenticated": True,
            "token_expires_in_seconds": max(0, int(entry.expires_at - time.monotonic())),
        }

    async def upload_content_image(
        self, alias: str, *, content: bytes, filename: str, content_type: str
    ) -> dict[str, Any]:
        data = await self._authorized_request(
            alias,
            "POST",
            "/cgi-bin/media/uploadimg",
            files={"media": (filename, content, content_type)},
        )
        url = data.get("url")
        if not isinstance(url, str) or not url:
            raise WeChatApiError("WeChat content-image upload returned no URL")
        return {"url": url.replace("http://", "https://", 1)}

    async def upload_cover(
        self, alias: str, *, content: bytes, filename: str, content_type: str
    ) -> dict[str, Any]:
        data = await self._authorized_request(
            alias,
            "POST",
            "/cgi-bin/material/add_material",
            params={"type": "thumb"},
            files={"media": (filename, content, content_type)},
        )
        media_id = data.get("media_id")
        if not isinstance(media_id, str) or not media_id:
            raise WeChatApiError("WeChat cover upload returned no media_id")
        return {"media_id": media_id, "url": data.get("url")}

    async def create_draft(self, alias: str, articles: list[DraftArticle]) -> dict[str, Any]:
        payload = {
            "articles": [article.model_dump(exclude_none=True) for article in articles],
        }
        data = await self._authorized_request(
            alias,
            "POST",
            "/cgi-bin/draft/add",
            json=payload,
        )
        media_id = data.get("media_id")
        if not isinstance(media_id, str) or not media_id:
            raise WeChatApiError("WeChat draft creation returned no media_id")
        return {"media_id": media_id}

    async def list_drafts(
        self, alias: str, *, offset: int, count: int, no_content: bool
    ) -> dict[str, Any]:
        return await self._authorized_request(
            alias,
            "POST",
            "/cgi-bin/draft/batchget",
            json={"offset": offset, "count": count, "no_content": int(no_content)},
        )

    async def get_draft(self, alias: str, *, media_id: str) -> dict[str, Any]:
        return await self._authorized_request(
            alias,
            "POST",
            "/cgi-bin/draft/get",
            json={"media_id": media_id},
        )

    async def publish_draft(self, alias: str, *, media_id: str) -> dict[str, Any]:
        data = await self._authorized_request(
            alias,
            "POST",
            "/cgi-bin/freepublish/submit",
            json={"media_id": media_id},
        )
        publish_id = data.get("publish_id")
        if publish_id is None or str(publish_id) == "":
            raise WeChatApiError("WeChat publish submission returned no publish_id")
        return {"publish_id": str(publish_id)}

    async def get_publish_status(self, alias: str, *, publish_id: str) -> dict[str, Any]:
        return await self._authorized_request(
            alias,
            "POST",
            "/cgi-bin/freepublish/get",
            json={"publish_id": publish_id},
        )

    async def _access_token(self, alias: str) -> str:
        self.account(alias)
        cached = self._tokens.get(alias)
        if cached and cached.expires_at > time.monotonic():
            return cached.value

        async with self._token_locks[alias]:
            cached = self._tokens.get(alias)
            if cached and cached.expires_at > time.monotonic():
                return cached.value

            account = self.accounts[alias]
            data = await self._raw_request(
                "GET",
                "/cgi-bin/token",
                params={
                    "grant_type": "client_credential",
                    "appid": account.app_id,
                    "secret": account.app_secret.get_secret_value(),
                },
            )
            self._raise_for_api_error(data)
            token = data.get("access_token")
            if not isinstance(token, str) or not token:
                raise WeChatApiError("WeChat token response contained no access_token")
            expires_in = int(data.get("expires_in", 7200))
            self._tokens[alias] = TokenEntry(
                value=token,
                expires_at=time.monotonic() + max(60, expires_in - 300),
            )
            return token

    async def _authorized_request(
        self,
        alias: str,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, tuple[str, bytes, str]] | None = None,
    ) -> dict[str, Any]:
        for attempt in range(2):
            token = await self._access_token(alias)
            request_params = dict(params or {})
            request_params["access_token"] = token
            data = await self._raw_request(
                method,
                path,
                params=request_params,
                json=json,
                files=files,
            )
            errcode = self._errcode(data)
            if errcode in TOKEN_ERROR_CODES and attempt == 0:
                self._tokens.pop(alias, None)
                continue
            self._raise_for_api_error(data)
            return data
        raise WeChatApiError("WeChat API token refresh retry failed")

    async def _raw_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, tuple[str, bytes, str]] | None = None,
    ) -> dict[str, Any]:
        try:
            response = await self.http.request(
                method,
                f"{self.base_url}{path}",
                params=params,
                json=json,
                files=files,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise WeChatApiError(f"WeChat API returned HTTP {exc.response.status_code}") from None
        except httpx.HTTPError:
            raise WeChatApiError("could not reach WeChat API") from None

        try:
            data = response.json()
        except ValueError:
            raise WeChatApiError("WeChat API returned invalid JSON") from None
        if not isinstance(data, dict):
            raise WeChatApiError("WeChat API returned an unexpected response")
        return data

    @staticmethod
    def _errcode(data: dict[str, Any]) -> int | None:
        value = data.get("errcode")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _raise_for_api_error(cls, data: dict[str, Any]) -> None:
        errcode = cls._errcode(data)
        if errcode in (None, 0):
            return
        errmsg = str(data.get("errmsg", "unknown error"))[:300]
        raise WeChatApiError(f"WeChat API error {errcode}: {errmsg}", errcode=errcode)

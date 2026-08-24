from __future__ import annotations

import base64
import binascii
import re
from pathlib import PurePath
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from .config import AccountCredential
from .models import DraftArticle, DraftResult, PublishResult, UploadResult
from .store import IdempotencyStore
from .wechat import WeChatApiError, WeChatClient

IDEMPOTENCY_KEY_RE = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}


class PublisherService:
    def __init__(
        self,
        client: WeChatClient,
        accounts: dict[str, AccountCredential],
        store: IdempotencyStore,
        *,
        allow_publish: bool,
        max_upload_bytes: int,
    ) -> None:
        self.client = client
        self.accounts = accounts
        self.store = store
        self.allow_publish = allow_publish
        self.max_upload_bytes = max_upload_bytes

    def account_summaries(self) -> list[dict[str, str]]:
        return [
            {
                "alias": account.alias,
                "name": account.name,
                "account_type": account.account_type,
            }
            for account in self.accounts.values()
        ]

    def decode_image(self, image_base64: str, filename: str, content_type: str) -> bytes:
        if content_type not in ALLOWED_IMAGE_TYPES:
            allowed = ", ".join(sorted(ALLOWED_IMAGE_TYPES))
            raise ToolError(f"unsupported image content type; use one of: {allowed}")
        if not filename or PurePath(filename).name != filename or "\x00" in filename:
            raise ToolError("filename must be a plain file name without path components")

        encoded = image_base64
        if image_base64.startswith("data:"):
            try:
                header, encoded = image_base64.split(",", 1)
            except ValueError:
                raise ToolError("invalid image data URL") from None
            if ";base64" not in header:
                raise ToolError("image data URL must use base64 encoding")

        try:
            content = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError):
            raise ToolError("image_base64 is not valid base64") from None
        if not content:
            raise ToolError("image is empty")
        if len(content) > self.max_upload_bytes:
            raise ToolError(f"image exceeds the {self.max_upload_bytes}-byte server limit")
        return content


def register_tools(mcp: FastMCP, service: PublisherService) -> None:
    read_only = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True)
    additive = ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    )
    idempotent_write = ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )

    @mcp.tool(annotations=read_only)
    async def wechat_list_accounts() -> list[dict[str, str]]:
        """List configured WeChat accounts without exposing credentials."""
        return service.account_summaries()

    @mcp.tool(annotations=read_only)
    async def wechat_check_account(account_alias: str) -> dict[str, Any]:
        """Verify that an account can obtain an access token from this server IP."""
        return await _call(service.client.check_account(account_alias))

    @mcp.tool(annotations=additive)
    async def wechat_upload_content_image(
        account_alias: str,
        image_base64: str,
        filename: str,
        content_type: str,
    ) -> dict[str, Any]:
        """Upload an inline article image and return its WeChat-hosted HTTPS URL."""
        content = service.decode_image(image_base64, filename, content_type)
        result = await _call(
            service.client.upload_content_image(
                account_alias,
                content=content,
                filename=filename,
                content_type=content_type,
            )
        )
        return UploadResult(
            account_alias=account_alias,
            kind="content_image",
            url=result["url"],
        ).model_dump(exclude_none=True)

    @mcp.tool(annotations=additive)
    async def wechat_upload_cover(
        account_alias: str,
        image_base64: str,
        filename: str,
        content_type: str,
    ) -> dict[str, Any]:
        """Upload a cover image as permanent material and return its media_id."""
        content = service.decode_image(image_base64, filename, content_type)
        result = await _call(
            service.client.upload_cover(
                account_alias,
                content=content,
                filename=filename,
                content_type=content_type,
            )
        )
        return UploadResult(
            account_alias=account_alias,
            kind="cover",
            media_id=result["media_id"],
            url=result.get("url"),
        ).model_dump(exclude_none=True)

    @mcp.tool(annotations=idempotent_write)
    async def wechat_create_draft(
        account_alias: str,
        articles: list[DraftArticle],
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Create a one-to-eight article draft; repeated idempotency keys reuse the first result."""
        _validate_idempotency_key(idempotency_key)
        if not 1 <= len(articles) <= 8:
            raise ToolError("articles must contain between 1 and 8 items")
        service.client.account(account_alias)

        cached = await service.store.get("create_draft", account_alias, idempotency_key)
        if cached:
            return DraftResult(
                account_alias=account_alias,
                media_id=str(cached["media_id"]),
                idempotency_key=idempotency_key,
                reused=True,
            ).model_dump()

        result = await _call(service.client.create_draft(account_alias, articles))
        stored = await service.store.put(
            "create_draft", account_alias, idempotency_key, {"media_id": result["media_id"]}
        )
        return DraftResult(
            account_alias=account_alias,
            media_id=str(stored["media_id"]),
            idempotency_key=idempotency_key,
        ).model_dump()

    @mcp.tool(annotations=read_only)
    async def wechat_list_drafts(
        account_alias: str,
        offset: int = 0,
        count: int = 20,
        no_content: bool = True,
    ) -> dict[str, Any]:
        """List drafts for an account. Set no_content=false only when full HTML is needed."""
        if offset < 0:
            raise ToolError("offset must be non-negative")
        if not 1 <= count <= 20:
            raise ToolError("count must be between 1 and 20")
        return await _call(
            service.client.list_drafts(
                account_alias,
                offset=offset,
                count=count,
                no_content=no_content,
            )
        )

    @mcp.tool(annotations=read_only)
    async def wechat_get_draft(account_alias: str, media_id: str) -> dict[str, Any]:
        """Get one draft by media_id."""
        if not media_id:
            raise ToolError("media_id is required")
        return await _call(service.client.get_draft(account_alias, media_id=media_id))

    @mcp.tool(annotations=idempotent_write)
    async def wechat_publish_draft(
        account_alias: str,
        media_id: str,
        idempotency_key: str,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        """Submit a draft for formal publication after explicit confirmation."""
        _validate_idempotency_key(idempotency_key)
        if not service.allow_publish:
            raise ToolError("formal publishing is disabled by MCP_ALLOW_PUBLISH")
        if not confirmed:
            raise ToolError(
                "formal publishing requires confirmed=true after explicit user approval"
            )
        if not media_id:
            raise ToolError("media_id is required")
        service.client.account(account_alias)

        cached = await service.store.get("publish_draft", account_alias, idempotency_key)
        if cached:
            return PublishResult(
                account_alias=account_alias,
                publish_id=str(cached["publish_id"]),
                idempotency_key=idempotency_key,
                reused=True,
            ).model_dump()

        result = await _call(service.client.publish_draft(account_alias, media_id=media_id))
        stored = await service.store.put(
            "publish_draft",
            account_alias,
            idempotency_key,
            {"publish_id": result["publish_id"]},
        )
        return PublishResult(
            account_alias=account_alias,
            publish_id=str(stored["publish_id"]),
            idempotency_key=idempotency_key,
        ).model_dump()

    @mcp.tool(annotations=read_only)
    async def wechat_get_publish_status(account_alias: str, publish_id: str) -> dict[str, Any]:
        """Query the asynchronous result of a formal publication submission."""
        if not publish_id:
            raise ToolError("publish_id is required")
        return await _call(service.client.get_publish_status(account_alias, publish_id=publish_id))


def _validate_idempotency_key(value: str) -> None:
    if not IDEMPOTENCY_KEY_RE.fullmatch(value):
        raise ToolError(
            "idempotency_key must be 8-128 characters using letters, digits, '.', '_', ':', or '-'"
        )


async def _call(awaitable: Any) -> Any:
    try:
        return await awaitable
    except WeChatApiError as exc:
        raise ToolError(str(exc)) from None

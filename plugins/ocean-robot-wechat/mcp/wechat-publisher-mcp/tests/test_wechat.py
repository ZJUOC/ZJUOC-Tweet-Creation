from __future__ import annotations

import json

import httpx
import pytest
from pydantic import SecretStr

from wechat_publisher_mcp.config import AccountCredential
from wechat_publisher_mcp.models import DraftArticle
from wechat_publisher_mcp.wechat import WeChatApiError, WeChatClient


def account() -> AccountCredential:
    return AccountCredential(
        alias="primary",
        name="Primary",
        app_id="wx-app",
        app_secret=SecretStr("super-secret"),
    )


@pytest.mark.asyncio
async def test_create_draft_caches_access_token() -> None:
    token_requests = 0
    draft_requests = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal token_requests, draft_requests
        if request.url.path == "/cgi-bin/token":
            token_requests += 1
            assert request.url.params["appid"] == "wx-app"
            assert request.url.params["secret"] == "super-secret"
            return httpx.Response(200, json={"access_token": "token-one", "expires_in": 7200})
        if request.url.path == "/cgi-bin/draft/add":
            draft_requests += 1
            assert request.url.params["access_token"] == "token-one"
            body = json.loads(request.content)
            assert body["articles"][0]["title"] == "Title"
            return httpx.Response(200, json={"media_id": f"draft-{draft_requests}"})
        raise AssertionError(f"unexpected path: {request.url.path}")

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = WeChatClient({"primary": account()}, http_client=http)
    article = DraftArticle(title="Title", content="<p>Body</p>", thumb_media_id="cover")

    first = await client.create_draft("primary", [article])
    second = await client.create_draft("primary", [article])
    await http.aclose()

    assert first == {"media_id": "draft-1"}
    assert second == {"media_id": "draft-2"}
    assert token_requests == 1


@pytest.mark.asyncio
async def test_refreshes_expired_token_once() -> None:
    tokens = iter(["expired-token", "fresh-token"])

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cgi-bin/token":
            return httpx.Response(200, json={"access_token": next(tokens), "expires_in": 7200})
        if request.url.params["access_token"] == "expired-token":
            return httpx.Response(200, json={"errcode": 40014, "errmsg": "invalid token"})
        return httpx.Response(200, json={"total_count": 0, "item_count": 0, "item": []})

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = WeChatClient({"primary": account()}, http_client=http)

    result = await client.list_drafts("primary", offset=0, count=20, no_content=True)
    await http.aclose()

    assert result["total_count"] == 0


@pytest.mark.asyncio
async def test_http_errors_do_not_expose_credentials() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="failure")

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = WeChatClient({"primary": account()}, http_client=http)

    with pytest.raises(WeChatApiError) as captured:
        await client.check_account("primary")
    await http.aclose()

    message = str(captured.value)
    assert "super-secret" not in message
    assert "wx-app" not in message
    assert message == "WeChat API returned HTTP 500"

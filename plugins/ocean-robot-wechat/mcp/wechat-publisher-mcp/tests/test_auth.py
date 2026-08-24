from __future__ import annotations

import httpx
import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from wechat_publisher_mcp.auth import BearerAuthMiddleware


@pytest.mark.asyncio
async def test_bearer_auth_middleware() -> None:
    async def endpoint(_request: object) -> JSONResponse:
        return JSONResponse({"ok": True})

    protected = BearerAuthMiddleware(
        Starlette(routes=[Route("/", endpoint)]),
        "test-token-0123456789abcdef",
    )
    transport = httpx.ASGITransport(app=protected)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        missing = await client.get("/")
        wrong = await client.get("/", headers={"Authorization": "Bearer wrong"})
        valid = await client.get(
            "/",
            headers={"Authorization": "Bearer test-token-0123456789abcdef"},
        )

    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert missing.headers["www-authenticate"] == "Bearer"
    assert valid.status_code == 200
    assert valid.json() == {"ok": True}

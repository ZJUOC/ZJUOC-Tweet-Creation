from __future__ import annotations

import asyncio
import socket

import httpx
import pytest
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from wechat_publisher_mcp.app import create_app
from wechat_publisher_mcp.config import Settings


def test_public_mcp_host_is_allowed(tmp_path: object) -> None:
    settings = Settings(
        _env_file=None,
        mcp_bearer_token="test-token-0123456789abcdef",
        mcp_public_base_url="http://203.0.113.10:29930",
        mcp_state_path=str(tmp_path / "state.db"),  # type: ignore[operator]
        wechat_app_id="wx-test",
        wechat_app_secret="secret",
    )

    app = create_app(settings)
    security = app.state.mcp.settings.transport_security

    assert security is not None
    assert security.enable_dns_rebinding_protection is True
    assert "203.0.113.10:29930" in security.allowed_hosts
    assert "http://203.0.113.10:29930" in security.allowed_origins


@pytest.mark.asyncio
async def test_streamable_http_lists_tools_and_enforces_publish_gate(tmp_path: object) -> None:
    token = "test-token-0123456789abcdef"
    settings = Settings(
        _env_file=None,
        mcp_bearer_token=token,
        mcp_state_path=str(tmp_path / "state.db"),  # type: ignore[operator]
        mcp_allow_publish=False,
        wechat_account_alias="primary",
        wechat_account_name="Primary",
        wechat_app_id="wx-test",
        wechat_app_secret="secret",
    )
    app = create_app(settings)

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve(sockets=[sock]))
    for _ in range(100):
        if server.started:
            break
        await asyncio.sleep(0.01)
    assert server.started

    try:
        async with (
            httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as http_client,
            streamable_http_client(f"http://127.0.0.1:{port}/mcp", http_client=http_client) as (
                read,
                write,
                _,
            ),
            ClientSession(read, write) as session,
        ):
            await session.initialize()
            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            assert "wechat_create_draft" in names
            assert "wechat_publish_draft" in names

            accounts = await session.call_tool("wechat_list_accounts", {})
            assert not accounts.isError
            assert accounts.structuredContent == {
                "result": [
                    {
                        "alias": "primary",
                        "name": "Primary",
                        "account_type": "subscription",
                    }
                ]
            }

            blocked = await session.call_tool(
                "wechat_publish_draft",
                {
                    "account_alias": "primary",
                    "media_id": "draft-media-id",
                    "idempotency_key": "publish:test:001",
                    "confirmed": True,
                },
            )
            assert blocked.isError
            assert "MCP_ALLOW_PUBLISH" in blocked.content[0].text
    finally:
        server.should_exit = True
        await asyncio.wait_for(task, timeout=5)

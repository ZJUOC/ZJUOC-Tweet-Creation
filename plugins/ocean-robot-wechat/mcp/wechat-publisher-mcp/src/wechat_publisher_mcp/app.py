from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from . import __version__
from .auth import BearerAuthMiddleware
from .config import Settings, load_accounts
from .store import IdempotencyStore
from .tools import PublisherService, register_tools
from .wechat import WeChatClient

SERVER_INSTRUCTIONS = (
    "Create drafts by default. Never call wechat_publish_draft unless the user explicitly asks "
    "for formal publication, confirms the target account and draft, and the server enables "
    "publishing. Upload inline images first and replace their HTML src values with returned URLs; "
    "upload a cover before creating a draft. Reuse stable idempotency keys to avoid duplicates."
)


def _transport_security(settings: Settings) -> TransportSecuritySettings:
    public_url = urlsplit(settings.mcp_public_base_url)
    allowed_hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    allowed_origins = [
        "http://127.0.0.1:*",
        "http://localhost:*",
        "http://[::1]:*",
    ]

    if public_url.netloc:
        public_host = public_url.netloc.rsplit("@", 1)[-1]
        public_origin = f"{public_url.scheme}://{public_host}"
        if public_host not in allowed_hosts:
            allowed_hosts.append(public_host)
        if public_origin not in allowed_origins:
            allowed_origins.append(public_origin)

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )


def create_app(
    settings: Settings | None = None,
    *,
    http_client: httpx.AsyncClient | None = None,
) -> Starlette:
    settings = settings or Settings()
    accounts = load_accounts(settings)
    store = IdempotencyStore(settings.mcp_state_path)
    wechat = WeChatClient(
        accounts,
        base_url=settings.wechat_api_base_url,
        http_client=http_client,
    )
    service = PublisherService(
        wechat,
        accounts,
        store,
        allow_publish=settings.mcp_allow_publish,
        max_upload_bytes=settings.max_upload_bytes,
    )

    mcp = FastMCP(
        "WeChat Publisher",
        instructions=SERVER_INSTRUCTIONS,
        host=settings.mcp_host,
        port=settings.mcp_port,
        stateless_http=True,
        json_response=True,
        streamable_http_path="/mcp",
        transport_security=_transport_security(settings),
    )
    register_tools(mcp, service)

    async def healthz(_: Request) -> JSONResponse:
        return JSONResponse(
            {
                "status": "ok",
                "service": "wechat-publisher-mcp",
                "version": __version__,
                "accounts": len(accounts),
                "formal_publish_enabled": settings.mcp_allow_publish,
            }
        )

    @asynccontextmanager
    async def lifespan(_: Starlette) -> AsyncIterator[None]:
        await store.initialize()
        async with mcp.session_manager.run():
            try:
                yield
            finally:
                await wechat.close()

    protected_mcp = BearerAuthMiddleware(
        mcp.streamable_http_app(),
        settings.mcp_bearer_token.get_secret_value(),
    )
    app = Starlette(
        routes=[
            Route("/healthz", healthz, methods=["GET"]),
            Mount("/", app=protected_mcp),
        ],
        lifespan=lifespan,
    )
    app.state.mcp = mcp
    app.state.publisher_service = service
    return app


app = create_app()

from __future__ import annotations

import uvicorn

from .app import create_app
from .config import Settings


def main() -> None:
    settings = Settings()
    uvicorn.run(
        create_app(settings),
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level=settings.log_level.lower(),
        proxy_headers=True,
        forwarded_allow_ips="127.0.0.1",
    )


if __name__ == "__main__":
    main()

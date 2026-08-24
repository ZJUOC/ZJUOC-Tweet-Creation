# WeChat Official Account Publisher MCP

English | [简体中文](README.zh.md) | [日本語](README.ja.md)

An MCP publishing service designed to run on a server with a stable public egress IP. It lets Codex and other MCP clients upload images, create WeChat Official Account drafts, and submit a draft for formal publication only after two independent confirmation gates.

## Current Status

v0.1.0 is ready to use. The complete image-rich draft workflow has been validated against a real subscription account.

- Supports one or more WeChat Official Accounts, selected through safe aliases
- Uploads inline images to the WeChat CDN and cover images as permanent media
- Creates, retrieves, and lists drafts with pagination
- Submits drafts for formal publication and checks asynchronous publication status
- Uses SQLite-backed idempotency records to prevent duplicate drafts or submissions after uncertain retries
- Disables formal publication by default; both the server flag and explicit client confirmation are required
- Exposes 9 MCP tools over Streamable HTTP with Bearer Token authentication
- Includes the `publish-wechat-remote` Skill for image, draft, and publication workflows
- Uses `uv` for Python environment management with the Aliyun PyPI mirror by default
- Uses the DaoCloud mirror for the default Docker base image

## Tech Stack

| Layer | Choice |
| --- | --- |
| Language | Python 3.12+ |
| MCP | MCP Python SDK / Streamable HTTP |
| HTTP | Starlette + Uvicorn + HTTPX |
| Configuration | Pydantic Settings |
| Idempotency store | SQLite |
| Package manager | uv |
| Deployment | Docker Compose + Caddy / Nginx |

## Run Locally

```bash
cp .env.example .env
uv sync
uv run wechat-publisher-mcp
```

Check service health:

```bash
curl http://127.0.0.1:8000/healthz
```

The MCP endpoint is `http://127.0.0.1:8000/mcp`. Every request except `/healthz` must include:

```text
Authorization: Bearer <MCP_BEARER_TOKEN>
```

## Configuration

Generate a dedicated MCP token first:

```bash
openssl rand -hex 32
```

Then configure `.env`:

```dotenv
MCP_BEARER_TOKEN=replace-with-a-long-random-token
MCP_PUBLIC_BASE_URL=https://wechat-mcp.example.com
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_ALLOW_PUBLISH=false
MCP_STATE_PATH=/data/state.db

WECHAT_ACCOUNT_ALIAS=primary
WECHAT_ACCOUNT_NAME=My Official Account
WECHAT_ACCOUNT_TYPE=subscription
WECHAT_APP_ID=wx_your_app_id
WECHAT_APP_SECRET=your_app_secret
```

`MCP_PUBLIC_BASE_URL` must match the root URL used by clients. Its hostname or IP address, including any non-standard port, is added to the MCP Host allowlist.

Configure multiple accounts through `WECHAT_ACCOUNTS_JSON`. See [.env.example](.env.example) for the single-account field template.

## MCP Tools

| Tool | Purpose | Writes data |
| --- | --- | ---: |
| `wechat_list_accounts` | List safe account summaries | No |
| `wechat_check_account` | Verify credentials and the server egress IP allowlist | No |
| `wechat_upload_content_image` | Upload an inline image and return its WeChat CDN URL | Yes |
| `wechat_upload_cover` | Upload a cover and return its permanent-media `media_id` | Yes |
| `wechat_create_draft` | Create a draft containing 1–8 articles | Idempotent |
| `wechat_list_drafts` | List drafts with pagination | No |
| `wechat_get_draft` | Retrieve a specific draft | No |
| `wechat_publish_draft` | Submit a draft for formal publication | Idempotent, confirmation required |
| `wechat_get_publish_status` | Check publication task status | No |

## Connect Codex

Expose the server token to the process that starts Codex:

```bash
export WECHAT_MCP_TOKEN='<server MCP_BEARER_TOKEN>'
```

Add the server to `~/.codex/config.toml` or a trusted project's `.codex/config.toml`:

```toml
[mcp_servers.wechat_publisher]
url = "https://wechat-mcp.example.com/mcp"
bearer_token_env_var = "WECHAT_MCP_TOKEN"
default_tools_approval_mode = "writes"
tool_timeout_sec = 90

[mcp_servers.wechat_publisher.tools.wechat_publish_draft]
approval_mode = "prompt"
```

Restart Codex, then use `/mcp` to verify the connection.

The companion Skill lives in [`skills/publish-wechat-remote`](skills/publish-wechat-remote). To install it locally, copy or link that directory into `~/.codex/skills/`.

## Docker Deployment

```bash
docker compose up -d --build
```

Compose binds the service to `127.0.0.1:8000` by default. Put Caddy or Nginx in front of it to provide HTTPS; [Caddyfile.example](Caddyfile.example) contains a minimal reverse-proxy configuration.

After deployment:

1. Set `MCP_PUBLIC_BASE_URL` to the correct public root URL.
2. Add the server's stable egress IP to the WeChat Official Account API allowlist.
3. Keep `MCP_ALLOW_PUBLISH=false` and call `wechat_check_account` first.
4. Complete one image-upload and draft-creation test.
5. Enable `MCP_ALLOW_PUBLISH=true` only when formal publication is genuinely required.

## Validation

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
```

## Security Boundaries

- Never commit `.env`, AppSecret values, access tokens, MCP tokens, or real article content.
- Public deployments must use HTTPS and must not expose the container port directly.
- Keep human confirmation in the formal publication path; ambiguous requests to “post to WeChat” should create drafts only.
- Rotate any MCP token or AppSecret that appears in chats, tickets, or logs.
- The server deliberately exposes no tool for deleting drafts or published articles.

## License

[MIT](LICENSE)

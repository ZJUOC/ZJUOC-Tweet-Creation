# Remote WeChat MCP setup

## Expected tools

| Tool | Purpose |
|---|---|
| `wechat_list_accounts` | Resolve configured account aliases |
| `wechat_check_account` | Verify credentials and IP white list |
| `wechat_upload_content_image` | Get a WeChat-hosted inline image URL |
| `wechat_upload_cover` | Get a cover `media_id` |
| `wechat_create_draft` | Create an idempotent draft |
| `wechat_list_drafts` | Discover existing drafts |
| `wechat_get_draft` | Inspect one draft |
| `wechat_publish_draft` | Submit an explicitly confirmed formal publication |
| `wechat_get_publish_status` | Query asynchronous publication status |

## Codex configuration

Set the client token in the shell, then configure Streamable HTTP:

```bash
export WECHAT_MCP_TOKEN='<server token>'
```

```toml
[mcp_servers.wechat_publisher]
url = "https://wechat-mcp.example.com/mcp"
bearer_token_env_var = "WECHAT_MCP_TOKEN"
default_tools_approval_mode = "writes"
tool_timeout_sec = 90

[mcp_servers.wechat_publisher.tools.wechat_publish_draft]
approval_mode = "prompt"
```

Restart Codex after changing MCP configuration.

## Server requirements

- Put the server's fixed egress IP in every target account's API IP white list.
- Store account credentials only in the server `.env` or secret manager.
- Keep the MCP endpoint behind HTTPS and Bearer authentication.
- Leave `MCP_ALLOW_PUBLISH=false` until draft creation succeeds.
- Rotate any secret copied into chat or logs before production.

## Image contract

Pass base64 bytes, a path-free filename, and one of `image/jpeg`, `image/png`, or `image/gif`. The default server upload limit is 2 MiB so the encoded MCP request remains below the stable SDK transport limit. Compress larger images before upload.

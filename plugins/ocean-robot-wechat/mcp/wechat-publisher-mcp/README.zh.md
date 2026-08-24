# 微信公众号发布 MCP · WeChat Publisher MCP

[English](README.md) | 简体中文 | [日本語](README.ja.md)

一个运行在固定公网出口上的微信公众号发布服务，让 Codex 或其他 MCP 客户端安全地上传图片、创建草稿，并在双重确认后提交正式发布。

## 当前状态

v0.1.0 已可用，完整的订阅号图文草稿链路已经通过真实账号验证。

- 支持单个或多个微信公众号，以安全别名选择目标账号
- 上传正文图片到微信 CDN，上传封面为永久素材
- 创建、查询和分页列出图文草稿
- 提交正式发布并查询异步发布状态
- SQLite 幂等记录，避免不确定重试产生重复草稿或重复发布
- 正式发布默认关闭，需要服务端开关和调用方确认同时满足
- Streamable HTTP + Bearer Token，提供 9 个 MCP 工具
- 附带 `publish-wechat-remote` Skill，定义图片、草稿和发布工作流
- `uv` 管理 Python 环境，默认使用阿里云 PyPI 镜像
- Docker 默认使用 DaoCloud 国内镜像加速

## 技术栈

| 层 | 选型 |
| --- | --- |
| 语言 | Python 3.12+ |
| MCP | MCP Python SDK / Streamable HTTP |
| HTTP | Starlette + Uvicorn + HTTPX |
| 配置 | Pydantic Settings |
| 幂等存储 | SQLite |
| 包管理 | uv |
| 部署 | Docker Compose + Caddy / Nginx |

## 启动

```bash
cp .env.example .env
uv sync
uv run wechat-publisher-mcp
```

健康检查：

```bash
curl http://127.0.0.1:8000/healthz
```

MCP 地址为 `http://127.0.0.1:8000/mcp`。除 `/healthz` 外，请求必须携带：

```text
Authorization: Bearer <MCP_BEARER_TOKEN>
```

## 配置

首先生成独立的 MCP Token：

```bash
openssl rand -hex 32
```

然后填写 `.env`：

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

`MCP_PUBLIC_BASE_URL` 必须与客户端实际访问的根地址一致。域名或 IP 以及非标准端口会进入 MCP Host 白名单。

多账号可以通过 `WECHAT_ACCOUNTS_JSON` 配置；单账号字段模板见 [.env.example](.env.example)。

## MCP 工具

| 工具 | 作用 | 写入 |
| --- | --- | ---: |
| `wechat_list_accounts` | 列出账号安全摘要 | 否 |
| `wechat_check_account` | 验证凭据和服务器出口 IP 白名单 | 否 |
| `wechat_upload_content_image` | 上传正文图片并返回微信 CDN URL | 是 |
| `wechat_upload_cover` | 上传封面并返回永久素材 `media_id` | 是 |
| `wechat_create_draft` | 创建 1–8 篇图文草稿 | 幂等 |
| `wechat_list_drafts` | 分页列出草稿 | 否 |
| `wechat_get_draft` | 获取指定草稿 | 否 |
| `wechat_publish_draft` | 提交正式发布 | 幂等、需确认 |
| `wechat_get_publish_status` | 查询发布任务状态 | 否 |

## 接入 Codex

先把服务器 Token 放入启动 Codex 的环境：

```bash
export WECHAT_MCP_TOKEN='<server MCP_BEARER_TOKEN>'
```

在 `~/.codex/config.toml` 或可信项目的 `.codex/config.toml` 中添加：

```toml
[mcp_servers.wechat_publisher]
url = "https://wechat-mcp.example.com/mcp"
bearer_token_env_var = "WECHAT_MCP_TOKEN"
default_tools_approval_mode = "writes"
tool_timeout_sec = 90

[mcp_servers.wechat_publisher.tools.wechat_publish_draft]
approval_mode = "prompt"
```

重启 Codex，然后使用 `/mcp` 检查连接。

配套 Skill 位于 [`skills/publish-wechat-remote`](skills/publish-wechat-remote)。需要本地安装时，可以将该目录复制或链接到 `~/.codex/skills/`。

## Docker 部署

```bash
docker compose up -d --build
```

Compose 默认只监听服务器的 `127.0.0.1:8000`。公网入口应通过 Caddy 或 Nginx 提供 HTTPS；[Caddyfile.example](Caddyfile.example) 给出了最小反向代理示例。

部署完成后：

1. 设置正确的 `MCP_PUBLIC_BASE_URL`。
2. 将服务器固定出口 IP 加入公众号接口 IP 白名单。
3. 保持 `MCP_ALLOW_PUBLISH=false`，先调用 `wechat_check_account`。
4. 完成一次图片上传和草稿测试。
5. 确实需要正式发布时，再开启 `MCP_ALLOW_PUBLISH=true`。

## 验证

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
```

## 安全边界

- 不要提交 `.env`、AppSecret、access token、MCP Token 或真实文章内容。
- 公网部署必须使用 HTTPS，不要直接暴露容器端口。
- 正式发布应保持人工确认；模糊的“发公众号”请求默认只创建草稿。
- MCP Token 或 AppSecret 出现在聊天、工单或日志后，应立即轮换。
- 服务不提供删除草稿或删除已发布文章的工具。

## License

[MIT](LICENSE)

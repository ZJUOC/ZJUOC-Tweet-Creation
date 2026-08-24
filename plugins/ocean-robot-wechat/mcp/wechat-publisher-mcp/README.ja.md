# WeChat公式アカウント Publisher MCP

[English](README.md) | [简体中文](README.zh.md) | 日本語

固定されたパブリック送信元IPを持つサーバー上で動作するMCP投稿サービスです。CodexなどのMCPクライアントから画像をアップロードし、WeChat公式アカウントの下書きを作成できます。正式公開は、独立した2段階の確認を通過した場合にのみ実行されます。

## 現在の状態

v0.1.0 は利用可能です。実際のサブスクリプションアカウントで、画像を含む下書き作成フロー全体を検証済みです。

- 1つまたは複数のWeChat公式アカウントに対応し、安全なエイリアスで対象を選択
- 本文画像をWeChat CDNへ、カバー画像を永続素材としてアップロード
- 下書きの作成、取得、ページネーション付き一覧表示
- 下書きの正式公開申請と、非同期の公開状態確認
- SQLiteの冪等性レコードにより、不確実な再試行での下書きや公開申請の重複を防止
- 正式公開はデフォルトで無効。サーバー側フラグとクライアント側の明示的な確認の両方が必要
- Streamable HTTPとBearer Token認証で9個のMCPツールを公開
- 画像、下書き、公開ワークフローを定義する `publish-wechat-remote` Skillを同梱
- Python環境は `uv` で管理し、デフォルトでAliyun PyPIミラーを使用
- DockerのベースイメージはデフォルトでDaoCloudミラーを使用

## 技術スタック

| レイヤー | 採用技術 |
| --- | --- |
| 言語 | Python 3.12+ |
| MCP | MCP Python SDK / Streamable HTTP |
| HTTP | Starlette + Uvicorn + HTTPX |
| 設定 | Pydantic Settings |
| 冪等性ストア | SQLite |
| パッケージ管理 | uv |
| デプロイ | Docker Compose + Caddy / Nginx |

## ローカルで起動

```bash
cp .env.example .env
uv sync
uv run wechat-publisher-mcp
```

ヘルスチェック：

```bash
curl http://127.0.0.1:8000/healthz
```

MCPエンドポイントは `http://127.0.0.1:8000/mcp` です。`/healthz` 以外のすべてのリクエストには次のヘッダーが必要です。

```text
Authorization: Bearer <MCP_BEARER_TOKEN>
```

## 設定

最初に専用のMCP Tokenを生成します。

```bash
openssl rand -hex 32
```

次に `.env` を設定します。

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

`MCP_PUBLIC_BASE_URL` は、クライアントが使用するルートURLと一致させてください。ホスト名またはIPアドレス、および標準外ポートはMCPのHost許可リストへ追加されます。

複数アカウントは `WECHAT_ACCOUNTS_JSON` で設定できます。単一アカウントのフィールド例は [.env.example](.env.example) を参照してください。

## MCPツール

| ツール | 用途 | データ書き込み |
| --- | --- | ---: |
| `wechat_list_accounts` | 安全なアカウント概要を一覧表示 | なし |
| `wechat_check_account` | 認証情報とサーバー送信元IP許可リストを検証 | なし |
| `wechat_upload_content_image` | 本文画像をアップロードし、WeChat CDN URLを返す | あり |
| `wechat_upload_cover` | カバー画像をアップロードし、永続素材の `media_id` を返す | あり |
| `wechat_create_draft` | 1〜8本の記事を含む下書きを作成 | 冪等 |
| `wechat_list_drafts` | 下書きをページネーション付きで一覧表示 | なし |
| `wechat_get_draft` | 指定した下書きを取得 | なし |
| `wechat_publish_draft` | 下書きの正式公開を申請 | 冪等、確認必須 |
| `wechat_get_publish_status` | 公開タスクの状態を確認 | なし |

## Codexへ接続

Codexを起動するプロセスへサーバーTokenを渡します。

```bash
export WECHAT_MCP_TOKEN='<server MCP_BEARER_TOKEN>'
```

`~/.codex/config.toml` または信頼済みプロジェクトの `.codex/config.toml` にサーバーを追加します。

```toml
[mcp_servers.wechat_publisher]
url = "https://wechat-mcp.example.com/mcp"
bearer_token_env_var = "WECHAT_MCP_TOKEN"
default_tools_approval_mode = "writes"
tool_timeout_sec = 90

[mcp_servers.wechat_publisher.tools.wechat_publish_draft]
approval_mode = "prompt"
```

Codexを再起動し、`/mcp` で接続を確認してください。

同梱のSkillは [`skills/publish-wechat-remote`](skills/publish-wechat-remote) にあります。ローカルへインストールする場合は、このディレクトリを `~/.codex/skills/` へコピーするかシンボリックリンクを作成してください。

## Dockerデプロイ

```bash
docker compose up -d --build
```

Composeはデフォルトでサービスを `127.0.0.1:8000` にのみバインドします。CaddyまたはNginxを前段に配置してHTTPSを提供してください。[Caddyfile.example](Caddyfile.example) に最小構成のリバースプロキシ例があります。

デプロイ後：

1. `MCP_PUBLIC_BASE_URL` を正しい公開ルートURLに設定します。
2. サーバーの固定送信元IPをWeChat公式アカウントAPIの許可リストへ追加します。
3. `MCP_ALLOW_PUBLISH=false` のまま、最初に `wechat_check_account` を呼び出します。
4. 画像アップロードと下書き作成を一度テストします。
5. 正式公開が本当に必要な場合にのみ `MCP_ALLOW_PUBLISH=true` を有効にします。

## 検証

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
```

## セキュリティ境界

- `.env`、AppSecret、access token、MCP Token、実際の記事本文をコミットしないでください。
- 公開環境では必ずHTTPSを使用し、コンテナのポートを直接公開しないでください。
- 正式公開には人による確認を残してください。「WeChatへ投稿」のような曖昧な依頼は、下書き作成として扱います。
- チャット、チケット、ログに現れたMCP TokenやAppSecretはローテーションしてください。
- 下書きや公開済み記事を削除するツールは、意図的に公開していません。

## ライセンス

[MIT](LICENSE)

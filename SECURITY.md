# 安全说明

不要通过 Issue、Pull Request 或仓库文件提交公众号 AppSecret、Bearer Token、访问令牌、`.env`、`state.db` 或成员个人隐私信息。

发现凭据泄漏时应立即在微信公众平台或对应服务中吊销并轮换，而不是仅删除 Git 文件。安全问题请通过仓库维护组织的私密联系方式报告。

公众号 MCP 默认 `MCP_ALLOW_PUBLISH=false`。任何正式发布或群发动作都需要在草稿复核后获得单独确认。

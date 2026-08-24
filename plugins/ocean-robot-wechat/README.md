# 海洋机器人公众号工坊

这个插件把协会推文工作流拆成五个可重复调用的部分：AI 可检索素材库、Ardot 原生组件、结构化文章规格、公众号安全 HTML 编译、草稿发布 MCP。

## 本地使用

1. 用插件内的 `ocean-robot-wechat` skill 查询组件和素材，确定单篇主风格并制作 Ardot 原生稿。
2. 运行 skill 的 `scripts/compile_wechat.py`，得到 `index.html` 和 `wechat.html`。
3. 在 Chrome 扩展管理页加载 `assets/chrome-extension`，进入公众号编辑器后点击“导入海机协推文”。
4. 需要草稿箱 API 时，复制 `.env.example` 到插件根目录 `.env`，设置 `MCP_BEARER_TOKEN`、`WECHAT_APP_ID`、`WECHAT_APP_SECRET`，运行 `scripts/launch-wechat-publisher-mcp`。

`MCP_ALLOW_PUBLISH` 默认关闭。正常工作流只创建草稿；正式群发必须单独确认。

# Ardot 原生设计规范

插件通过 `https://ardot.tencent.com/mcp` 使用 Ardot Remote MCP。安装插件后按提示完成 OAuth；若工具未出现，执行：

```bash
codex mcp add ardot-remote --url https://ardot.tencent.com/mcp
codex mcp login ardot-remote
```

## 原生要求

- 文章、模板和组件使用 Frame、Text、变量、图片 Fill、SVG 与 Component 构建。
- 不把整页 HTML 或截图当作最终可编辑源。
- 可复用组件以 `组件｜` 命名。
- 位图先注册并上传，再作为组件 Frame 的图片 Fill。
- Logo 只上传仓库原图，不重绘。
- 在页面根节点插入新画板前先查找可用空间。

## 示例 Ardot 文件

- 文件：`https://ardot.tencent.com/file/718241568273827`
- 示例页面：`10:1`
- 文章 Frame：`10:13`
- 布局组件库：`10:22`
- AI 素材库：`23:1`

节点映射位于 `examples/recruitment-2026-lively/ardot-component-map.json`。该文件是示例和回归参考，不应把这些节点 ID 硬编码到新文章中。

## 双轨交付

Ardot 文件承担多人编辑和视觉复核；`article.json` 与编译器承担确定性 HTML 交付。两条轨道使用同一套组件 ID 和素材 ID。

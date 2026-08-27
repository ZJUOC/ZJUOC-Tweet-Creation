# 成熟工作流

## 1. 输入合同

每篇推文开始前明确：文章类型、目标读者、核心行动、已核验事实、正文草稿、照片、Logo、二维码和发布截止时间。缺失事实保留显式占位符，不让 AI 猜测奖项、参数、时间或联系人。

## 2. 检索优先

AI 先运行组件和素材查询：

```bash
python3 scripts/components.py recommend recruitment
python3 scripts/assets.py recommend recruitment
python3 scripts/assets.py search "声呐 competition"
```

只有现有素材不能表达具体机器人、实验或活动时才生成新素材。新素材必须加入注册表，不能只散落在某篇文章目录中。

## 3. 风格路由

- 招新和社群：`watercolor-cutout`。
- 活动和外场：`paper-cut`。
- 科普和机器人档案：`technical-line`。
- `editorial-decor` 只做辅助标点。

单篇文章只使用一套主插画风格。小插图约每两到三个内容区块出现一次。

## 4. Ardot 原生稿

Ardot 是可编辑设计源。使用原生 Frame、Text、变量、图片 Fill 和 Component；HTML 不是 Ardot 的替代品。组件使用稳定中文名并以 `组件｜` 开头。

每篇文章保存：Ardot 文件 URL、页面 ID、文章 Frame ID、组件库 ID、素材库 ID 和组件节点映射。

## 5. 结构化规格与编译

文章以 `article.json` 保存。编译器生成：

- `index.html`：本地手机预览，可包含预览交互。
- `wechat.html`：公众号安全的内联样式 HTML，不含脚本。
- `compile-report.json`：组件数量、滑动图库和错误报告。

```bash
python3 scripts/compile_wechat.py article.json --output output --check
```

需要更灵动、紧凑的版式时，优先使用富排版区块：`hero_rich`、`manifesto_rich`、`heading_rich`、`story_collage`、`path_rich`、`swipe_gallery_rich`、`bridge_rich`、`departments_rich` 与 `join_rich`。它们通过不对称留白、边缘切图、图片叠放和露出下一屏的滑动区建立节奏，不依赖 JavaScript。

## 6. QA 闸门

交付前必须通过：

- 所有本地图片存在。
- 可复用切图是真 Alpha，四角透明。
- Logo 外不出现深蓝或藏青色系统色。
- 横向滑动区域露出下一张边缘，并有“左右滑动”提示。
- 正文在 390px 左右手机宽度下无溢出。
- Ardot 关键区块完成截图复核。
- 二维码来自用户材料且可扫描。
- `compile_wechat.py --check` 与 `assets.py validate` 均通过。

## 7. 交付与发布

优先交付 Ardot 原生稿、`article.json`、`wechat.html` 和素材目录。公众号 API 默认只创建草稿。正式发布、群发或替换线上内容必须获得单独确认。

## 8. 新素材回流

通过 QA 的新素材加入 `references/assets.json`，记录稳定 ID、主题、风格、用途、路径和来源；随后创建 Ardot 可复用组件。这样下一篇文章可以直接检索复用。

## 9. A4 海报衍生

当同一活动需要线下宣传单时，以 `examples/recruitment-2026-a4-poster` 为起点复用文章事实、协会 Logo、已注册切图和用户提供的二维码。海报脚本输出 300 dpi PNG 与印刷 PDF；二维码只允许裁切和等比缩放，不生成、不美化、不替换。

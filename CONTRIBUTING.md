# 贡献指南

## 新组件或素材

1. 先确认现有注册表中没有同义素材。
2. 使用浅色品牌色，不在 Logo 外引入深蓝。
3. 位图切图必须是真透明 PNG；优先使用 SVG 表达线稿和装饰。
4. 更新 `references/assets.json` 或 `references/components.json`。
5. 在 Ardot 中建立对应的可复用组件。
6. 运行 `./scripts/check.sh`。

## 新示例文章

示例目录至少包含 `article.json`、所需素材、`index.html`、`wechat.html` 和 `compile-report.json`。不要提交真实 AppSecret、访问令牌、私有群二维码或未获授权的内部照片。

## 技能发现路径

`skills/ocean-robot-wechat` 是插件技能目录的符号链接，给 `npx skills add` 和 [skills.sh](https://skills.sh/) 用。技能正文、素材和脚本只维护在 `plugins/ocean-robot-wechat/skills/ocean-robot-wechat/`。不要把内容复制到仓库根 `skills/`。

## 提交前

```bash
./scripts/bootstrap.sh
./scripts/check.sh
```

Pull Request 中说明文章类型、主视觉风格、新增组件 ID、Ardot 节点映射和 QA 结果。

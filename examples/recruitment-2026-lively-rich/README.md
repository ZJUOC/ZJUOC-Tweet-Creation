# 灵动丰富版推文

这是 2026 纳新推文的 20 组件参考实现，用于测试富排版区块、两组横向滑动画廊、真实活动照片、冰蓝透明插图和双二维码报名区。

```bash
python3 ../../plugins/ocean-robot-wechat/skills/ocean-robot-wechat/scripts/compile_wechat.py \
  article.json --output . --check
```

- `article.json` 是结构化内容源。
- `index.html` 是手机预览。
- `wechat.html` 是无脚本、内联样式的公众号交付版。
- `ardot-component-map.json` 保存 Ardot 文件与节点映射。
- `compile-report.json` 和 `qa-report.json` 保存自动与视觉 QA 结果。

示例照片和二维码来自协会提供的原推文素材；二维码不得生成或替换。

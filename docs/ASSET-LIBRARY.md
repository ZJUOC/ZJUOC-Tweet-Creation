# 水机素材库

机器可读注册表位于：

```text
plugins/ocean-robot-wechat/skills/ocean-robot-wechat/references/assets.json
```

## 查询

```bash
skill=plugins/ocean-robot-wechat/skills/ocean-robot-wechat
python3 "$skill/scripts/assets.py" list
python3 "$skill/scripts/assets.py" list --style technical-line
python3 "$skill/scripts/assets.py" search "ROV training"
python3 "$skill/scripts/assets.py" recommend popular-science
python3 "$skill/scripts/assets.py" validate
```

## ID 规则

- `cutout.watercolor.*`：水彩真透明 PNG。
- `cutout.paper.*`：纸雕真透明 PNG。
- `line.*`：技术线稿 SVG。
- `decor.*`：编辑装饰 SVG。

ID 一旦发布应保持稳定。文件路径可以迁移，但必须同步更新注册表。

## 新增透明切图

生成式工具如果不能直接输出真透明，请让主体位于纯 `#F000F0` 隔离背景上，并确保内部开口同样被洋红填满：

```bash
./scripts/chroma_to_alpha.sh input.png output.png
python3 ./scripts/assets.py validate
```

在 `#FFF9F2` 和 `#EAF7F8` 两种底色上检查边缘。任何棋盘格、洋红边、断裂细节或四角不透明都视为失败。

## 品牌规则

允许的编辑色为 `#2E4148 #53666C #6DA7CF #8CCCD3 #EAF7F8 #F09A7C #F2D6A2 #F7FBFA` 和白色。协会 Logo 内部深蓝属于受保护原图，不是可复用色票。

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
python3 "$skill/scripts/assets.py" list --style hard-tech
python3 "$skill/scripts/assets.py" search "ROV training"
python3 "$skill/scripts/assets.py" search "机械 推进器 hardware-deep-dive"
python3 "$skill/scripts/assets.py" recommend project-update --style hard-tech
python3 "$skill/scripts/assets.py" validate
```

## ID 规则

- `cutout.watercolor.*`：水彩真透明 PNG。
- `cutout.paper.*`：纸雕真透明 PNG。
- `cutout.hard-tech.*`：硬核科技真透明 PNG，表达完成度、感知、自主与竞赛能力。
- `cutout.mechanical.*`：机械工业真透明 PNG，表达结构、拆解、制造与运维。
- `line.*`：技术线稿 SVG。
- `decor.*`：编辑装饰 SVG。

ID 一旦发布应保持稳定。文件路径可以迁移，但必须同步更新注册表。

单篇推文只选一个主风格。`hard-tech` 用于呈现“这套系统能做什么”，`mechanical-industrial` 用于解释“它如何构成、连接、维修或操作”；技术线稿与编辑装饰可以少量辅助，但不要把水彩和工业组件随机混排。

## 新增透明切图

生成式工具如果不能直接输出真透明，请让主体位于纯 `#F000F0` 隔离背景上，并确保内部开口同样被洋红填满：

```bash
./scripts/chroma_to_alpha.sh input.png output.png
python3 ./scripts/assets.py validate
```

在 `#FFF9F2` 和 `#EAF7F8` 两种底色上检查边缘。任何棋盘格、洋红边、断裂细节或四角不透明都视为失败。

## 品牌规则

允许的编辑色为 `#2E4148 #53666C #6DA7CF #8CCCD3 #EAF7F8 #F09A7C #F2D6A2 #F7FBFA` 和白色。协会 Logo 内部深蓝属于受保护原图，不是可复用色票。

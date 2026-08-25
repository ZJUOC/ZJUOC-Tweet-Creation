#!/usr/bin/env python3
"""Render a compact visual QA board for raster asset style families."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "references" / "assets.json"
STYLE_LABELS = {
    "watercolor-cutout": ("卡通水彩", "轻松、亲和、招新与社群"),
    "paper-cut": ("纸雕叙事", "活动、外场与团队故事"),
    "hard-tech": ("硬核科技", "整机能力、感知、自主与竞赛"),
    "mechanical-industrial": ("机械工业", "结构、拆解、制造与运维"),
    "clay-miniature": ("黏土模型", "招新、培训与实验室日常"),
    "isometric-system": ("等轴工程", "任务链、系统关系与测试流程"),
    "aqua-glass": ("冰蓝透明", "声呐、导航、数据链与未来感知"),
}
BACKGROUNDS = ["#FFF9F2", "#EAF7F8"]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "STHeiti Medium.ttc" if bold else "STHeiti Light.ttc"
    path = Path("/System/Library/Fonts") / name
    return ImageFont.truetype(str(path), size=size)


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    result = image.copy()
    result.thumbnail(size, Image.Resampling.LANCZOS)
    return result


def render(output: Path) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    groups = {
        style: [
            item
            for item in catalog["assets"]
            if item["style"] == style and item["path"].lower().endswith(".png")
        ]
        for style in STYLE_LABELS
    }

    width = 1600
    margin = 80
    gap = 30
    group_heights = {
        style: 110 + max(1, math.ceil(len(items) / 3)) * 320
        for style, items in groups.items()
    }
    height = 150 + sum(group_heights.values()) + 50
    board = Image.new("RGB", (width, height), "#F7FBFA")
    draw = ImageDraw.Draw(board)
    draw.text((margin, 45), "水机 AI 素材库 · 多风格组件", fill="#2E4148", font=font(46, True))
    draw.text((margin, 103), "同一主题，按内容语义选择风格；不要把不同质感随机混用。", fill="#53666C", font=font(24))

    y = 150
    for index, (style, (label, description)) in enumerate(STYLE_LABELS.items()):
        items = groups[style]
        group_h = group_heights[style]
        draw.rounded_rectangle((margin, y, width - margin, y + group_h - 24), radius=28, fill="#FFFFFF", outline="#DCECED", width=2)
        draw.text((margin + 34, y + 28), label, fill="#2E4148", font=font(32, True))
        draw.text((margin + 220, y + 36), description, fill="#667A80", font=font(20))
        card_y = y + 92
        column_count = min(3, max(1, len(items)))
        card_w = (width - 2 * margin - 68 - (column_count - 1) * gap) // column_count
        for item_index, item in enumerate(items):
            column = item_index % 3
            row = item_index // 3
            x = margin + 34 + column * (card_w + gap)
            item_y = card_y + row * 320
            art_h = 235
            bg = BACKGROUNDS[(index + item_index) % len(BACKGROUNDS)]
            draw.rounded_rectangle((x, item_y, x + card_w, item_y + art_h), radius=22, fill=bg)
            with Image.open(ROOT / item["path"]) as source:
                art = contain(source.convert("RGBA"), (card_w - 34, art_h - 28))
            px = x + (card_w - art.width) // 2
            py = item_y + (art_h - art.height) // 2
            board.paste(art, (px, py), art)
            title = item["title"].replace(label, "").strip()
            draw.text((x + 4, item_y + art_h + 17), title, fill="#2E4148", font=font(21, True))
            draw.text((x + 4, item_y + art_h + 51), item["id"], fill="#7A9095", font=font(14))
        y += group_h

    output.parent.mkdir(parents=True, exist_ok=True)
    board.save(output, quality=94)
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.output)


if __name__ == "__main__":
    main()

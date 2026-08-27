#!/usr/bin/env python3
"""Compile a structured Ocean Robot article into preview and WeChat-safe HTML."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

INK = "#2E4148"
BODY = "#53666C"
SKY = "#6DA7CF"
AQUA = "#8CCCD3"
PALE = "#EAF7F8"
CORAL = "#F09A7C"
SAND = "#F2D6A2"
FOAM = "#F7FBFA"
DEEP_BLUE = re.compile(r"#(?:0054A7|003B6F|002B55|0B2D45)|\bnavy\b", re.I)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def style(**values: str) -> str:
    return ";".join(f"{key.replace('_', '-')}:{value}" for key, value in values.items())


def image(item: dict[str, Any], extra: str = "") -> str:
    return (
        f'<img src="{esc(item["src"])}" alt="{esc(item.get("alt", ""))}" '
        f'style="display:block;width:100%;height:100%;object-fit:cover;{extra}"/>'
    )


def paragraphs(items: list[str]) -> str:
    return "".join(
        f'<p style="margin:0 0 12px;line-height:1.72;font-size:16px;color:{BODY};letter-spacing:.02em;">{esc(item)}</p>'
        for item in items
    )


def render_block(block: dict[str, Any]) -> str:
    kind = block["type"]
    component = esc(block.get("component", f"layout.{kind.replace('_', '-')}"))
    if kind == "hero_rich":
        bg, spot = block["images"]
        tags = "".join(
            f'<span style="display:inline-block;margin:0 5px 6px 0;padding:6px 10px;border:1px solid rgba(46,65,72,.16);border-radius:999px;background:rgba(247,251,250,.82);color:{INK};font-size:11px;font-weight:800;letter-spacing:.03em;">{esc(item)}</span>'
            for item in block.get("tags", [])
        )
        return f'''<section data-component="{component}" style="position:relative;height:610px;background:{PALE};overflow:hidden;">
<img src="{esc(bg['src'])}" alt="{esc(bg.get('alt', ''))}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;"/>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(247,251,250,.16) 0%,rgba(247,251,250,.05) 48%,rgba(46,65,72,.32) 100%);"></div>
<div style="position:absolute;left:22px;right:22px;top:22px;">
  <div style="display:flex;align-items:center;gap:9px;margin-bottom:24px;"><img src="{esc(block['logo'])}" alt="浙江大学学生海洋机器人协会 Logo" style="width:42px;height:42px;object-fit:contain;border-radius:50%;background:white;box-shadow:0 5px 16px rgba(46,65,72,.12);"/><div style="font-size:10px;line-height:1.45;color:{INK};font-weight:800;letter-spacing:.12em;">{esc(block.get('eyebrow', 'ZJU OCEAN ROBOT'))}</div></div>
  <div style="font-size:14px;color:{CORAL};font-weight:900;letter-spacing:.14em;margin-bottom:7px;">{esc(block.get('kicker', '2026 纳新'))}</div>
  <h1 style="margin:0;width:91%;font-size:41px;line-height:1.04;color:{INK};font-weight:950;letter-spacing:-.06em;text-shadow:0 2px 0 rgba(255,255,255,.62);">{esc(block['title'])}</h1>
  <p style="margin:14px 0 12px;width:82%;font-size:15px;line-height:1.66;color:{BODY};font-weight:650;">{esc(block['subtitle'])}</p>
  <div>{tags}</div>
</div>
<div style="position:absolute;left:-46px;bottom:28px;width:190px;height:126px;transform:rotate(-8deg);filter:drop-shadow(0 12px 15px rgba(46,65,72,.13));">{image(spot, 'object-fit:contain;')}</div>
<div style="position:absolute;right:18px;bottom:22px;padding:8px 13px;border-radius:999px;background:{CORAL};color:white;font-size:12px;font-weight:900;letter-spacing:.06em;box-shadow:0 8px 18px rgba(240,154,124,.28);">向下潜入 ↓</div>
</section>'''
    if kind == "manifesto_rich":
        facts = "".join(
            f'<div style="display:inline-block;vertical-align:top;width:31%;margin-right:2%;white-space:normal;"><div style="font-size:23px;line-height:1;color:{SKY};font-weight:950;">{esc(item["value"])}</div><div style="margin-top:5px;font-size:11px;line-height:1.45;color:{BODY};">{esc(item["label"])}</div></div>'
            for item in block.get("facts", [])
        )
        return f'''<section data-component="{component}" style="position:relative;padding:34px 24px 26px;background:white;overflow:hidden;">
<div style="position:absolute;right:-34px;top:30px;width:122px;height:122px;border:18px solid {PALE};border-radius:50%;opacity:.72;"></div>
<div style="position:relative;font-size:12px;color:{CORAL};font-weight:900;letter-spacing:.16em;margin-bottom:10px;">{esc(block.get('eyebrow', 'WHO WE ARE'))}</div>
<div style="position:relative;font-size:27px;line-height:1.28;color:{INK};font-weight:950;letter-spacing:-.035em;margin-bottom:14px;">{esc(block['lead'])}</div>
<div style="position:relative;">{paragraphs(block['paragraphs'])}</div>
<div style="position:relative;margin-top:21px;padding:16px 13px;border-top:1px solid {AQUA};border-bottom:1px solid {AQUA};white-space:nowrap;">{facts}</div>
</section>'''
    if kind == "heading_rich":
        return f'''<section data-component="{component}" style="position:relative;min-height:168px;padding:34px 23px 16px;background:{FOAM};overflow:hidden;">
<div style="position:absolute;left:-42px;top:24px;width:165px;height:82px;border-radius:50%;background:{PALE};transform:rotate(-10deg);"></div>
<div style="position:absolute;right:-30px;top:4px;width:178px;height:150px;filter:drop-shadow(0 10px 13px rgba(46,65,72,.12));transform:rotate({esc(block.get('rotate', '4deg'))});">{image(block['image'], 'object-fit:contain;')}</div>
<div style="position:relative;max-width:65%;"><div style="display:inline-block;padding:6px 10px;border-radius:999px;background:{CORAL};color:white;font-size:11px;font-weight:900;letter-spacing:.1em;">{esc(block['number'])}</div>
<h2 style="margin:10px 0 0;font-size:28px;line-height:1.18;color:{INK};font-weight:950;letter-spacing:-.04em;">{esc(block['title'])}</h2>
<div style="margin-top:8px;width:52px;height:4px;border-radius:4px;background:{AQUA};"></div></div>
</section>'''
    if kind == "story_collage":
        imgs = block["images"]
        return f'''<section data-component="{component}" style="position:relative;height:430px;background:white;overflow:hidden;">
<div style="position:absolute;left:0;top:10px;width:84%;height:272px;border-radius:0 18px 18px 0;overflow:hidden;box-shadow:0 10px 26px rgba(46,65,72,.12);">{image(imgs[0])}</div>
<div style="position:absolute;right:-7px;top:218px;width:49%;height:150px;padding:6px;background:white;border-radius:12px;transform:rotate(3deg);box-shadow:0 11px 22px rgba(46,65,72,.14);overflow:hidden;">{image(imgs[1])}</div>
<div style="position:absolute;left:23px;bottom:25px;width:49%;font-size:13px;line-height:1.6;color:{BODY};"><span style="display:block;margin-bottom:5px;color:{CORAL};font-size:11px;font-weight:900;letter-spacing:.12em;">{esc(block.get('label', 'FIELD NOTE'))}</span>{esc(block['caption'])}</div>
</section>'''
    if kind == "path_rich":
        rows = []
        for index, item in enumerate(block["items"]):
            offset = 0 if index in (0, 4) else (28 if index in (1, 3) else 54)
            rows.append(
                f'<div style="position:relative;margin:0 0 8px {offset}px;display:flex;align-items:center;gap:10px;"><div style="width:28px;height:28px;border-radius:50%;background:{CORAL};color:white;text-align:center;line-height:28px;font-size:12px;font-weight:900;">{index + 1}</div><div style="padding:8px 13px;border-radius:999px;background:{PALE};color:{INK};font-size:13px;font-weight:850;box-shadow:0 5px 12px rgba(46,65,72,.06);">{esc(item)}</div></div>'
            )
        return f'''<section data-component="{component}" style="position:relative;padding:4px 24px 25px;background:white;overflow:hidden;">
<div style="position:absolute;left:43px;top:14px;width:180px;height:210px;border:2px dashed {AQUA};border-radius:50%;opacity:.42;transform:rotate(13deg);"></div>
<div style="position:relative;">{''.join(rows)}</div></section>'''
    if kind == "swipe_gallery_rich":
        slides = "".join(
            f'<div style="display:inline-block;vertical-align:top;width:88%;margin-right:11px;white-space:normal;"><div style="position:relative;height:236px;border-radius:18px;overflow:hidden;background:{PALE};box-shadow:0 10px 24px rgba(46,65,72,.11);">{image(item)}<div style="position:absolute;left:0;right:0;bottom:0;padding:30px 14px 12px;background:linear-gradient(180deg,rgba(46,65,72,0),rgba(46,65,72,.68));color:white;font-size:13px;line-height:1.5;font-weight:750;">{esc(item.get("caption", ""))}</div></div></div>'
            for item in block["images"]
        )
        return f'''<section data-component="{component}" style="padding:6px 0 28px 22px;background:white;">
<div style="display:flex;justify-content:space-between;align-items:center;margin:0 22px 10px 0;"><div style="font-size:12px;color:{INK};font-weight:900;letter-spacing:.08em;">{esc(block.get('label', '现场切片'))}</div><div style="font-size:10px;color:{CORAL};font-weight:800;">左右滑动 →</div></div>
<div style="overflow-x:auto;overflow-y:hidden;white-space:nowrap;-webkit-overflow-scrolling:touch;padding:0 1px 8px;">{slides}</div></section>'''
    if kind == "bridge_rich":
        align = block.get("align", "right")
        image_pos = "right:-35px" if align == "right" else "left:-35px"
        text_margin = "margin-right:112px" if align == "right" else "margin-left:112px"
        return f'''<section data-component="{component}" style="position:relative;min-height:154px;padding:24px;background:{PALE};overflow:hidden;">
<div style="position:absolute;{image_pos};top:2px;width:190px;height:148px;filter:drop-shadow(0 10px 14px rgba(46,65,72,.12));">{image(block['image'], 'object-fit:contain;')}</div>
<div style="position:relative;{text_margin};"><div style="font-size:11px;color:{CORAL};font-weight:900;letter-spacing:.12em;margin-bottom:7px;">{esc(block.get('label', 'NEXT DIVE'))}</div><div style="font-size:20px;line-height:1.35;color:{INK};font-weight:950;">{esc(block['title'])}</div><div style="margin-top:7px;font-size:13px;line-height:1.55;color:{BODY};">{esc(block.get('text', ''))}</div></div>
</section>'''
    if kind == "departments_rich":
        rows = []
        colors = [PALE, "#FFF3ED", "#EEF8F3", "#FFF8E7"]
        for index, item in enumerate(block["items"]):
            side = "margin-left:30px" if index % 2 else "margin-right:30px"
            rows.append(
                f'<div style="{side};margin-bottom:12px;padding:16px 17px;background:{colors[index % len(colors)]};border-radius:18px 18px {"5px 18px" if index % 2 else "18px 5px"};box-shadow:0 7px 16px rgba(46,65,72,.06);"><div style="display:flex;align-items:center;gap:9px;margin-bottom:5px;"><span style="font-size:11px;color:{CORAL};font-weight:950;">0{index+1}</span><span style="font-size:17px;color:{INK};font-weight:950;">{esc(item["name"])}</span></div><div style="font-size:13px;line-height:1.62;color:{BODY};">{esc(item["description"])}</div></div>'
            )
        return f'<section data-component="{component}" style="padding:4px 22px 28px;background:white;">{"".join(rows)}</section>'
    if kind == "join_rich":
        steps = "".join(
            f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:11px;"><div style="flex:0 0 27px;height:27px;border-radius:50%;background:{CORAL};color:white;text-align:center;line-height:27px;font-size:12px;font-weight:950;">{i+1}</div><div style="padding-top:2px;font-size:14px;line-height:1.55;color:{INK};font-weight:700;">{esc(item)}</div></div>'
            for i, item in enumerate(block["steps"])
        )
        qrs = "".join(
            f'<div style="display:inline-block;vertical-align:top;width:45%;margin-right:5%;text-align:center;white-space:normal;"><div style="aspect-ratio:1/1;background:white;padding:8px;border-radius:15px;box-shadow:0 10px 22px rgba(46,65,72,.10);">{image(item)}</div><div style="margin-top:7px;font-size:12px;color:{BODY};font-weight:800;">{esc(item.get("caption", ""))}</div></div>'
            for item in block["qrs"]
        )
        return f'''<section data-component="{component}" style="position:relative;padding:32px 22px 34px;background:linear-gradient(145deg,{PALE},#F7FBFA 65%,#FFF3ED);overflow:hidden;">
<div style="position:absolute;right:-35px;top:-20px;width:170px;height:135px;opacity:.88;transform:rotate(8deg);">{image(block['image'], 'object-fit:contain;')}</div>
<div style="position:relative;width:70%;font-size:12px;color:{CORAL};font-weight:900;letter-spacing:.15em;">READY TO DIVE?</div><h2 style="position:relative;width:74%;margin:7px 0 18px;font-size:29px;line-height:1.18;color:{INK};font-weight:950;letter-spacing:-.04em;">{esc(block['title'])}</h2>
<div style="position:relative;">{steps}</div><div style="position:relative;white-space:nowrap;margin-top:20px;">{qrs}</div></section>'''
    if kind == "hero_collage":
        imgs = block["images"]
        return f'''<section data-component="{component}" style="position:relative;padding:18px 20px 24px;background:{FOAM};overflow:hidden;">
<div style="position:absolute;right:-42px;top:-34px;width:134px;height:134px;border:2px solid {AQUA};border-radius:50%;opacity:.55;"></div>
<div style="font-size:11px;letter-spacing:.16em;color:{CORAL};font-weight:700;margin-bottom:10px;">{esc(block.get("eyebrow", "ZJU OCEAN ROBOT"))}</div>
<h1 style="margin:0;line-height:1.14;font-size:32px;color:{INK};letter-spacing:-.035em;font-weight:800;">{esc(block["title"])}</h1>
<p style="margin:10px 0 16px;line-height:1.65;font-size:15px;color:{BODY};">{esc(block["subtitle"])}</p>
<div style="position:relative;height:256px;">
  <div style="position:absolute;left:0;top:8px;width:68%;height:180px;transform:rotate(-1deg);box-shadow:0 9px 22px rgba(46,65,72,.12);background:white;padding:6px;border-radius:8px;overflow:hidden;">{image(imgs[0])}</div>
  <div style="position:absolute;right:-2px;top:90px;width:48%;height:146px;transform:rotate(1.2deg);box-shadow:0 9px 22px rgba(46,65,72,.12);background:white;padding:6px;border-radius:8px;overflow:hidden;">{image(imgs[1])}</div>
  <div style="position:absolute;left:14px;bottom:0;padding:7px 13px;border-radius:999px;background:{SAND};font-size:12px;color:{INK};font-weight:700;transform:rotate(-.6deg);">让机器人真正下水 ↘</div>
</div></section>'''
    if kind == "open_text":
        return f'<section data-component="{component}" style="padding:24px 25px 12px;background:white;">{paragraphs(block["paragraphs"])}</section>'
    if kind == "heading":
        return f'''<section data-component="{component}" style="padding:28px 22px 12px;background:white;">
<div style="display:inline-block;padding:6px 11px;border-radius:999px;background:{PALE};color:{SKY};font-size:11px;font-weight:800;letter-spacing:.08em;transform:rotate(-.6deg);">{esc(block["number"])}</div>
<h2 style="margin:8px 0 0;font-size:23px;line-height:1.3;color:{INK};letter-spacing:-.02em;">{esc(block["title"])}</h2>
</section>'''
    if kind == "swipe_gallery":
        width = 84
        slides = "".join(
            f'<div style="display:inline-block;vertical-align:top;width:{width}%;margin-right:10px;white-space:normal;">'
            f'<div style="height:194px;background:{PALE};overflow:hidden;border-radius:8px;">{image(item)}</div>'
            f'<div style="padding:8px 3px 0;font-size:12px;color:{BODY};line-height:1.5;">{esc(item.get("caption", ""))}</div></div>'
            for item in block["images"]
        )
        return f'''<section data-component="{component}" style="padding:4px 0 18px 22px;background:white;">
<div style="margin:0 22px 6px 0;text-align:right;font-size:10px;color:{CORAL};letter-spacing:.08em;">左右滑动查看更多 →</div>
<div style="overflow-x:auto;overflow-y:hidden;white-space:nowrap;-webkit-overflow-scrolling:touch;padding-bottom:5px;">{slides}</div>
</section>'''
    if kind == "offset_pair":
        imgs = block["images"]
        return f'''<section data-component="{component}" style="position:relative;height:350px;padding:8px 22px;background:{FOAM};overflow:hidden;">
<div style="position:absolute;left:22px;top:14px;width:66%;height:210px;transform:rotate(-1deg);background:white;padding:6px;border-radius:8px;overflow:hidden;box-shadow:0 9px 22px rgba(46,65,72,.11);">{image(imgs[0])}</div>
<div style="position:absolute;right:18px;bottom:28px;width:54%;height:178px;transform:rotate(1.2deg);background:white;padding:6px;border-radius:8px;overflow:hidden;box-shadow:0 9px 22px rgba(46,65,72,.11);">{image(imgs[1])}</div>
<div style="position:absolute;left:24px;bottom:30px;width:35%;font-size:12px;line-height:1.55;color:{BODY};">{esc(block.get("caption", "一起调试，也一起把机器人捞回来。"))}</div>
</section>'''
    if kind == "path":
        steps = "".join(
            f'<span style="display:inline-block;margin:0 6px 6px 0;padding:7px 10px;background:{PALE};border-radius:8px;color:{INK};font-size:12px;font-weight:700;">{esc(item)}</span>'
            for item in block["items"]
        )
        return f'<section data-component="{component}" style="padding:12px 24px 18px;background:white;border-left:3px solid {AQUA};">{steps}</section>'
    if kind == "text":
        return f'<section data-component="{component}" style="padding:0 25px 16px;background:white;">{paragraphs(block["paragraphs"])}</section>'
    if kind == "spot_note":
        align = block.get("align", "right")
        margin = "margin-left:auto" if align == "right" else "margin-right:auto"
        return f'''<section data-component="{component}" style="padding:0 24px 14px;background:white;">
<div style="width:78px;{margin};transform:rotate(.6deg);">{image(block["image"], "object-fit:contain;")}</div>
<div style="max-width:225px;{margin};margin-top:-5px;padding:8px 11px;background:{SAND};border-radius:8px;color:{INK};font-size:12px;line-height:1.5;transform:rotate(-.4deg);">{esc(block["text"])}</div>
</section>'''
    if kind == "departments":
        rows = []
        for index, item in enumerate(block["items"]):
            side = "margin-left:18px" if index % 2 else "margin-right:18px"
            rows.append(
                f'<div style="{side};margin-bottom:9px;padding:14px 16px;background:{PALE};border-left:3px solid {AQUA};border-radius:8px;">'
                f'<div style="font-size:16px;font-weight:800;color:{INK};margin-bottom:5px;">{esc(item["name"])}</div>'
                f'<div style="font-size:14px;line-height:1.62;color:{BODY};">{esc(item["description"])}</div></div>'
            )
        return f'<section data-component="{component}" style="padding:6px 22px 20px;background:white;">{"".join(rows)}</section>'
    if kind == "join_steps":
        steps = "".join(
            f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:9px;"><div style="flex:0 0 26px;height:26px;border-radius:50%;background:{CORAL};color:white;text-align:center;line-height:26px;font-weight:800;">{i+1}</div><div style="padding-top:2px;font-size:14px;line-height:1.6;color:{INK};">{esc(item)}</div></div>'
            for i, item in enumerate(block["steps"])
        )
        qrs = "".join(
            f'<div style="display:inline-block;vertical-align:top;width:46%;margin:0 2%;text-align:center;white-space:normal;"><div style="aspect-ratio:1/1;background:white;padding:7px;border-radius:8px;">{image(item)}</div><div style="font-size:12px;color:{BODY};margin-top:6px;">{esc(item.get("caption", ""))}</div></div>'
            for item in block["qrs"]
        )
        return f'''<section data-component="{component}" style="padding:22px 22px 28px;background:{PALE};">
<h2 style="margin:0 0 15px;color:{INK};font-size:24px;">加入方式</h2>{steps}
<div style="white-space:nowrap;margin:16px -2% 0;">{qrs}</div></section>'''
    if kind == "footer":
        return f'''<footer data-component="{component}" style="padding:24px 24px 30px;text-align:center;background:{FOAM};">
<img src="{esc(block["logo"])}" alt="浙江大学学生海洋机器人协会 Logo" style="width:60px;height:60px;object-fit:contain;border-radius:50%;margin:0 auto 10px;"/>
<div style="font-size:15px;font-weight:800;color:{INK};">浙江大学学生海洋机器人协会</div>
<div style="margin-top:7px;font-size:11px;line-height:1.6;color:{BODY};">{esc(block.get("credits", ""))}</div>
</footer>'''
    raise ValueError(f"Unsupported block type: {kind}")


def compile_article(spec: dict[str, Any]) -> str:
    blocks = "".join(render_block(block) for block in spec["blocks"])
    return f'<article data-article="ocean-robot-wechat" style="max-width:390px;margin:0 auto;background:white;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Hiragino Sans GB,Microsoft YaHei,sans-serif;overflow:hidden;">{blocks}</article>'


def validate(inner: str, spec: dict[str, Any], spec_path: Path) -> list[str]:
    errors: list[str] = []
    if "<script" in inner.lower():
        errors.append("scripts are not allowed")
    if DEEP_BLUE.search(inner):
        errors.append("deep blue found outside protected logo artwork")
    if "overflow-x:auto" not in inner:
        errors.append("missing horizontal swipe behavior")
    if inner.count("data-component=") < 6:
        errors.append("too few semantic components")
    if re.search(r'<img(?![^>]*\balt=")[^>]*>', inner, re.I):
        errors.append("an image is missing alt text")
    if re.search(r'<(?:link|style)\b', inner, re.I):
        errors.append("wechat fragment must use inline styles only")
    for block in spec["blocks"]:
        assets = block.get("images", []) + block.get("qrs", [])
        if block.get("image"):
            assets.append(block["image"])
        for item in assets:
            source = spec_path.parent / item["src"]
            if not source.is_file():
                errors.append(f"missing asset: {item['src']}")
        if block.get("logo") and not (spec_path.parent / block["logo"]).is_file():
            errors.append(f"missing asset: {block['logo']}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    inner = compile_article(spec)
    errors = validate(inner, spec, spec_path)
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        source_label = str(spec_path.relative_to(args.output.resolve()))
    except ValueError:
        source_label = str(spec_path)
    preview = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(spec["title"])}</title><style>html{{background:#DDE9E8}}body{{margin:0;padding:28px 0}}@media(max-width:430px){{body{{padding:0}}}}</style></head><body>{inner}</body></html>'''
    (args.output / "index.html").write_text(preview, encoding="utf-8")
    (args.output / "wechat.html").write_text(inner, encoding="utf-8")
    report = {
        "title": spec["title"],
        "source": source_label,
        "component_count": inner.count("data-component="),
        "swipe_gallery_count": inner.count("overflow-x:auto"),
        "errors": errors,
        "status": "pass" if not errors else "fail",
    }
    (args.output / "compile-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.check and errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

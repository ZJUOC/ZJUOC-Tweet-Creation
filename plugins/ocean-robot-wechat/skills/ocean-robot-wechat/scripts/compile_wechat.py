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

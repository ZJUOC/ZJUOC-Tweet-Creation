#!/usr/bin/env python3
"""Search, recommend, validate, and preview the Ocean Robot asset library."""

from __future__ import annotations

import argparse
import json
import os
import re
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "references" / "assets.json"
STYLE_LABELS = {
    "watercolor-cutout": "卡通水彩",
    "paper-cut": "纸雕叙事",
    "hard-tech": "硬核科技",
    "mechanical-industrial": "机械工业",
    "clay-miniature": "黏土模型",
    "isometric-system": "等轴工程",
    "aqua-glass": "冰蓝透明",
    "technical-line": "技术线稿",
    "editorial-decor": "编辑装饰",
}


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def emit(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def compact(item: dict[str, Any]) -> dict[str, Any]:
    return {key: item[key] for key in ("id", "title", "kind", "style", "path", "uses")}


def list_assets(catalog: dict[str, Any], style: str | None, kind: str | None) -> None:
    items = catalog["assets"]
    if style:
        items = [item for item in items if item["style"] == style]
    if kind:
        items = [item for item in items if item["kind"] == kind]
    emit([compact(item) for item in items])


def search_assets(catalog: dict[str, Any], query: str) -> None:
    tokens = [token.lower() for token in re.split(r"\s+", query.strip()) if token]
    ranked: list[tuple[int, dict[str, Any]]] = []
    for item in catalog["assets"]:
        haystack = " ".join(str(value) for value in [item["id"], item["title"], item["kind"], item["style"], *item.get("subjects", []), *item.get("uses", [])]).lower()
        score = sum(3 if token in item["id"].lower() else 1 for token in tokens if token in haystack)
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    emit([compact(item) | {"score": score} for score, item in ranked])


def recommend(catalog: dict[str, Any], article_type: str, style: str | None) -> None:
    routes = catalog["style_routes"]
    styles = [style] if style else routes.get(article_type)
    if not styles:
        raise SystemExit(f"Unknown article type: {article_type}. Available: {', '.join(sorted(routes))}")
    items = [item for item in catalog["assets"] if item["style"] in styles and (article_type in item.get("uses", []) or "all" in item.get("uses", []))]
    emit({"article_type": article_type, "dominant_style": styles[0], "fallback_style": styles[1:] or None, "assets": [compact(item) for item in items]})


def validate(catalog: dict[str, Any]) -> None:
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for item in catalog["assets"]:
        if item["id"] in seen_ids:
            errors.append(f"duplicate id: {item['id']}")
        if item["path"] in seen_paths:
            errors.append(f"duplicate path: {item['path']}")
        seen_ids.add(item["id"]); seen_paths.add(item["path"])
        path = ROOT / item["path"]
        if not path.exists():
            errors.append(f"missing: {item['id']} -> {path}")
            continue
        if path.suffix.lower() == ".svg":
            source = path.read_text(encoding="utf-8")
            if "viewBox=" not in source:
                errors.append(f"SVG missing viewBox: {item['id']}")
            if "<text" in source.lower():
                errors.append(f"SVG contains text node: {item['id']}")
            if re.search(r"#0054a7|navy|deep-blue", source, flags=re.I):
                errors.append(f"SVG contains forbidden deep blue: {item['id']}")
        if item.get("alpha_required"):
            try:
                from PIL import Image
                with Image.open(path) as image:
                    if "A" not in image.getbands():
                        errors.append(f"PNG has no alpha channel: {item['id']}")
                        continue
                    alpha = image.getchannel("A")
                    low, high = alpha.getextrema()
                    if low != 0 or high != 255:
                        errors.append(f"PNG alpha range is {low}..{high}: {item['id']}")
                    corners = [alpha.getpixel((0, 0)), alpha.getpixel((image.width - 1, 0)), alpha.getpixel((0, image.height - 1)), alpha.getpixel((image.width - 1, image.height - 1))]
                    if max(corners) > 4:
                        errors.append(f"PNG corners are not transparent: {item['id']} {corners}")
            except ImportError:
                errors.append("Pillow unavailable; cannot validate PNG alpha")
                break
    report = {"ok": not errors, "asset_count": len(catalog["assets"]), "errors": errors}
    emit(report)
    if errors:
        raise SystemExit(1)


def preview(catalog: dict[str, Any], output: Path) -> None:
    cards = []
    for item in catalog["assets"]:
        uri = Path(os.path.relpath(ROOT / item["path"], output.parent)).as_posix()
        tags = " ".join([item["style"], item["kind"], *item.get("subjects", []), *item.get("uses", [])])
        cards.append(f'''<article class="card" data-search="{escape(tags.lower())}" data-style="{escape(item['style'])}">
<div class="art"><img src="{escape(uri)}" alt="{escape(item['title'])}"></div>
<div class="meta"><span>{escape(STYLE_LABELS.get(item['style'], item['style']))}</span><h2>{escape(item['title'])}</h2><code>{escape(item['id'])}</code></div></article>''')
    styles = sorted({item["style"] for item in catalog["assets"]})
    buttons = ['<button class="active" data-style="">全部</button>'] + [
        f'<button data-style="{escape(style)}">{escape(STYLE_LABELS.get(style, style))}</button>'
        for style in styles
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    html = f'''<!doctype html><meta charset="utf-8"><title>水机 AI 素材库</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#f7fbfa;color:#2e4148;font:15px/1.5 system-ui,-apple-system,sans-serif}}header{{position:sticky;top:0;z-index:2;padding:24px 5vw 18px;background:rgba(247,251,250,.95);backdrop-filter:blur(14px);border-bottom:1px solid #dceced}}h1{{margin:0 0 12px;font-size:30px}}.tools{{display:flex;gap:10px;flex-wrap:wrap}}input{{flex:1 1 360px;max-width:680px;border:1px solid #bcdde0;border-radius:999px;padding:12px 18px;background:white;font:inherit}}.filters{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}button{{border:1px solid #bcdde0;border-radius:999px;padding:7px 13px;background:white;color:#53666c;font:inherit;cursor:pointer}}button.active{{border-color:#f09a7c;background:#fff1eb;color:#a84e39}}main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:18px;padding:24px 5vw 64px}}.card{{overflow:hidden;border:1px solid #dceced;border-radius:22px;background:white;box-shadow:0 8px 24px rgba(46,65,72,.06)}}.art{{aspect-ratio:1;background:linear-gradient(135deg,#fff9f2,#eaf7f8);display:grid;place-items:center;padding:16px}}.art img{{max-width:100%;max-height:100%;object-fit:contain}}.meta{{padding:14px 16px 18px}}.meta span{{font-size:12px;color:#d66f58;text-transform:uppercase}}h2{{font-size:17px;margin:4px 0 7px}}code{{font-size:11px;color:#61777d;word-break:break-all}}.hide{{display:none}}</style>
<header><h1>水机 AI 素材库 · {len(catalog['assets'])}</h1><div class="tools"><input id="q" placeholder="搜索：ROV、声呐、机械臂、项目进展…"></div><div class="filters">{''.join(buttons)}</div></header><main>{''.join(cards)}</main>
<script>let active='';const cards=[...document.querySelectorAll('.card')];function filter(){{const v=q.value.trim().toLowerCase();cards.forEach(c=>c.classList.toggle('hide',(active&&c.dataset.style!==active)||(v&&!c.dataset.search.includes(v))))}}q.oninput=filter;document.querySelectorAll('button').forEach(b=>b.onclick=()=>{{document.querySelector('button.active').classList.remove('active');b.classList.add('active');active=b.dataset.style;filter()}})</script>'''
    output.write_text(html, encoding="utf-8")
    print(output)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    ls = commands.add_parser("list"); ls.add_argument("--style"); ls.add_argument("--kind")
    find = commands.add_parser("search"); find.add_argument("query")
    rec = commands.add_parser("recommend"); rec.add_argument("article_type"); rec.add_argument("--style")
    commands.add_parser("validate")
    pre = commands.add_parser("preview"); pre.add_argument("--output", type=Path, required=True)
    return root


def main() -> None:
    args = parser().parse_args(); catalog = load_catalog()
    if args.command == "list": list_assets(catalog, args.style, args.kind)
    elif args.command == "search": search_assets(catalog, args.query)
    elif args.command == "recommend": recommend(catalog, args.article_type, args.style)
    elif args.command == "validate": validate(catalog)
    elif args.command == "preview": preview(catalog, args.output)


if __name__ == "__main__":
    main()

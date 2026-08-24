#!/usr/bin/env python3
"""Query the Ocean Robot WeChat component registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "references" / "components.json"


def load_catalog() -> dict[str, Any]:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def component_map(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {component["id"]: component for component in catalog["components"]}


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def list_components(catalog: dict[str, Any], kind: str | None) -> None:
    components = catalog["components"]
    if kind:
        components = [item for item in components if item["kind"] == kind]
    print_json(
        [
            {
                "id": item["id"],
                "kind": item["kind"],
                "title": item["title"],
                "asset": item.get("asset"),
            }
            for item in components
        ]
    )


def show_component(catalog: dict[str, Any], component_id: str) -> None:
    components = component_map(catalog)
    if component_id not in components:
        raise SystemExit(f"Unknown component: {component_id}")
    print_json(components[component_id])


def recommend(catalog: dict[str, Any], article_type: str) -> None:
    recommendations = catalog["recommendations"]
    if article_type not in recommendations:
        available = ", ".join(sorted(recommendations))
        raise SystemExit(f"Unknown article type: {article_type}. Available: {available}")
    components = component_map(catalog)
    print_json([components[item] for item in recommendations[article_type]])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List registered components")
    list_parser.add_argument(
        "--kind", choices=["brand", "spot", "visual", "block", "layout"]
    )

    show_parser = subparsers.add_parser("show", help="Show one component")
    show_parser.add_argument("component_id")

    recommend_parser = subparsers.add_parser(
        "recommend", help="Recommend components for an article type"
    )
    recommend_parser.add_argument("article_type")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    catalog = load_catalog()

    if args.command == "list":
        list_components(catalog, args.kind)
    elif args.command == "show":
        show_component(catalog, args.component_id)
    elif args.command == "recommend":
        recommend(catalog, args.article_type)


if __name__ == "__main__":
    main()

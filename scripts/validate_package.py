#!/usr/bin/env python3
"""Validate the distributable repository without requiring Codex internals."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "ocean-robot-wechat"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    errors: list[str] = []
    manifest = read_json(PLUGIN / ".codex-plugin" / "plugin.json")
    marketplace = read_json(ROOT / ".agents" / "plugins" / "marketplace.json")

    if manifest.get("name") != PLUGIN.name:
        errors.append("plugin folder and manifest name differ")
    plugin_skill = PLUGIN / "skills" / "ocean-robot-wechat"
    canonical_skill = ROOT / "skills" / "ocean-robot-wechat"
    if not (plugin_skill / "SKILL.md").exists():
        errors.append("plugin skill entrypoint is missing")
    if not canonical_skill.is_symlink():
        errors.append("skills/ocean-robot-wechat must be a symlink for npx skills discovery")
    elif canonical_skill.resolve() != plugin_skill.resolve():
        errors.append("skills/ocean-robot-wechat must resolve to the plugin skill directory")
    elif not (canonical_skill / "SKILL.md").exists():
        errors.append("canonical skills/ocean-robot-wechat/SKILL.md is missing")
    if manifest.get("mcpServers") and not (PLUGIN / manifest["mcpServers"]).resolve().exists():
        errors.append("plugin mcpServers path is missing")
    entries = {item["name"]: item for item in marketplace.get("plugins", [])}
    entry = entries.get(PLUGIN.name)
    if not entry:
        errors.append("marketplace entry is missing")
    elif entry.get("source", {}).get("path") != "./plugins/ocean-robot-wechat":
        errors.append("marketplace source path is incorrect")

    tracked = subprocess.run(
        ["git", "ls-files", "--cached"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    machine_path_patterns = ("/Users/", "/private/tmp/", "file:///Users/")
    secret_patterns = [
        re.compile(r"gh[opurs]_[A-Za-z0-9_]{20,}"),
        re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"WECHAT_APP_SECRET=(?!your_app_secret|package-test-secret-not-for-production)\S+"),
        re.compile(r"MCP_BEARER_TOKEN=(?!generate-a-long-random-token|replace-with-a-long-random-token|package-test-token-not-for-production)\S+"),
    ]
    for relative in tracked:
        parts = Path(relative).parts
        if Path(relative).name in {".env", "state.db"} or any(
            part in {".venv", "__pycache__"} for part in parts
        ):
            errors.append(f"forbidden tracked path: {relative}")
        path = ROOT / relative
        audit_exempt = {"scripts/check.sh", "scripts/validate_package.py"}
        if relative not in audit_exempt and path.is_file() and path.stat().st_size < 2_000_000:
            try:
                source = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(pattern in source for pattern in machine_path_patterns):
                errors.append(f"machine-local path in tracked file: {relative}")
            if any(pattern.search(source) for pattern in secret_patterns):
                errors.append(f"possible secret in tracked file: {relative}")

    previews = [
        ROOT / "examples" / "asset-library" / "index.html",
        ROOT / "examples" / "asset-library-multistyle" / "index.html",
    ]
    for preview in previews:
        preview_source = preview.read_text(encoding="utf-8")
        for src in re.findall(r'<img[^>]+src="([^"]+)"', preview_source):
            if src.startswith(("file:", "/")):
                errors.append(f"non-portable preview image source: {preview}: {src}")
            elif not (preview.parent / src).resolve().exists():
                errors.append(f"missing preview image source: {preview}: {src}")

    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps({"ok": True, "plugin": manifest["name"], "version": manifest["version"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

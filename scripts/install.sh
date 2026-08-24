#!/usr/bin/env bash
set -euo pipefail

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is required: https://openai.com/codex/" >&2
  exit 2
fi

codex plugin marketplace add ZJUOC/ZJUOC-Tweet-Creation --ref main
codex plugin add ocean-robot-wechat@zjuoc

echo "Installed ocean-robot-wechat. Start a new Codex task to load it."

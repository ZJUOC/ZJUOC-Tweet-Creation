#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON_BIN:-$repo_root/.venv/bin/python}"

if [[ ! -x "$python_bin" ]]; then
  python_bin="$(command -v python3 || true)"
fi
if [[ -z "$python_bin" ]]; then
  echo "Python 3 is required." >&2
  exit 2
fi
if ! "$python_bin" -c 'import PIL' >/dev/null 2>&1; then
  echo "Pillow is required. Run ./scripts/bootstrap.sh first." >&2
  exit 2
fi

skill_root="$repo_root/plugins/ocean-robot-wechat/skills/ocean-robot-wechat"
example_root="$repo_root/examples/recruitment-2026-lively"
rich_example_root="$repo_root/examples/recruitment-2026-lively-rich"

"$python_bin" "$repo_root/scripts/validate_package.py"
"$python_bin" "$skill_root/scripts/assets.py" validate
"$python_bin" -m unittest discover -s "$skill_root/tests" -v
"$python_bin" "$skill_root/scripts/compile_wechat.py" \
  "$example_root/article.json" --output "$example_root" --check
"$python_bin" "$skill_root/scripts/compile_wechat.py" \
  "$rich_example_root/article.json" --output "$rich_example_root" --check

if command -v uv >/dev/null 2>&1; then
  publisher_root="$repo_root/plugins/ocean-robot-wechat/mcp/wechat-publisher-mcp"
  (
    cd "$publisher_root"
    NO_PROXY="127.0.0.1,localhost" \
      no_proxy="127.0.0.1,localhost" \
      MCP_BEARER_TOKEN="package-test-token-not-for-production" \
      WECHAT_APP_ID="wx-package-test" \
      WECHAT_APP_SECRET="package-test-secret-not-for-production" \
      uv run --group dev pytest
  )
else
  echo "uv not found; skipped optional WeChat publisher MCP tests."
fi

echo "All package checks passed."

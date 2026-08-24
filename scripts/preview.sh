#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
port="${PORT:-8765}"

echo "Asset library: http://127.0.0.1:${port}/examples/asset-library/index.html"
echo "Multi-style library: http://127.0.0.1:${port}/examples/asset-library-multistyle/index.html"
echo "Example article: http://127.0.0.1:${port}/examples/recruitment-2026-lively/index.html"
cd "$repo_root"
exec python3 -m http.server "$port" --bind 127.0.0.1

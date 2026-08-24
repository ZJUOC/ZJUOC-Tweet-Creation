#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "usage: $0 INPUT OUTPUT [SIMILARITY] [BLEND]" >&2
  exit 2
fi

input_path=$1
output_path=$2
similarity=${3:-0.40}
blend=${4:-0.02}

mkdir -p "$(dirname "$output_path")"
ffmpeg -hide_banner -loglevel error -y \
  -i "$input_path" \
  -vf "colorkey=0xF000F0:${similarity}:${blend},format=rgba" \
  "$output_path"

echo "$output_path"

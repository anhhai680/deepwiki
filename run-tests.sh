#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if command -v uv >/dev/null 2>&1; then
  uv run -m pytest -q "$@"
else
  python -m pytest -q "$@"
fi



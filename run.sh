#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py
exec python3 -m http.server "${1:-8650}" --bind 127.0.0.1 --directory webapp

#!/usr/bin/env bash
# Fetch data for all Signal Rooms.
# Usage: ./scripts/fetch_all.sh
# Optional: set FRED_API_KEY env var for live mortgage rates (Housing room).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"

echo "Signal Rooms — fetch all data"
echo "Root: $ROOT"
echo "---"

python3 "$SCRIPTS/fetch_gold.py"
python3 "$SCRIPTS/fetch_gpu.py"
python3 "$ROOT/rooms/oil-gas/fetch_data.py"
python3 "$ROOT/rooms/housing/fetch_data.py"

echo "---"
echo "All rooms updated."

#!/usr/bin/env python3
"""Run the Gold room fetch script from the unified scripts/ runner.

Note: Gold depends on heavier Python deps (yfinance/pandas). On some local macOS
installs we intentionally don't install those. In that case we skip Gold so the
other rooms can still refresh.
"""

import subprocess, os, sys

GOLD_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rooms", "gold", "fetch_data.py")

print("=== fetch_gold.py ===")
try:
    result = subprocess.run([sys.executable, GOLD_SCRIPT], check=True)
    sys.exit(result.returncode)
except subprocess.CalledProcessError as e:
    print(f"  [WARN] Gold fetch failed (skipping): {e}")
    sys.exit(0)

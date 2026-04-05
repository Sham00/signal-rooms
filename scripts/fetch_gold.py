#!/usr/bin/env python3
"""Run the Gold room fetch script from the unified scripts/ runner."""
import subprocess, os, sys

GOLD_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rooms", "gold", "fetch_data.py")

print("=== fetch_gold.py ===")
result = subprocess.run([sys.executable, GOLD_SCRIPT], check=True)
sys.exit(result.returncode)

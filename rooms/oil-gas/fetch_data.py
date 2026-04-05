#!/usr/bin/env python3
"""Fetch Oil & Gas room data and write to ./data/*.json.

Safe for periodic runs (GitHub Actions / cron). No API keys required.
Uses Stooq for daily futures proxies where available.

Outputs:
- data/summary.json
- data/prices_30d.json

Run:
  python3 rooms/oil-gas/fetch_data.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request

ROOM_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOM_DIR, "data")

SYMBOLS = {
    "wti": {"stooq": "cl.f", "name": "WTI Crude", "symbol": "CL=F"},
    "brent": {"stooq": "co.f", "name": "Brent", "symbol": "BZ=F"},
    "natgas": {"stooq": "ng.f", "name": "Henry Hub Nat Gas", "symbol": "NG=F"},
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_stooq_daily_csv(symbol: str) -> list[dict]:
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    req = Request(url, headers={"User-Agent": "signal-rooms/1.0"})
    with urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="replace")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # header: Date,Open,High,Low,Close,Volume
    out = []
    for ln in lines[1:]:
        parts = ln.split(",")
        if len(parts) < 5:
            continue
        date_s = parts[0]
        close_s = parts[4]
        try:
            v = float(close_s)
        except ValueError:
            continue
        out.append({"t": date_s, "v": v})
    return out


def pct_change(a: float, b: float) -> float:
    if a == 0:
        return 0.0
    return (b - a) / a * 100.0


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    updated_at = utc_now_iso()

    series = {}
    summary = {
        "asOf": None,
        "updatedAt": updated_at,
        "source": "stooq",
    }

    for key, meta in SYMBOLS.items():
        rows = fetch_stooq_daily_csv(meta["stooq"])
        if not rows:
            continue
        last30 = rows[-30:]
        series[key] = last30

        price = float(last30[-1]["v"])
        prev = float(last30[-2]["v"]) if len(last30) >= 2 else price
        chg = pct_change(prev, price)

        summary[key] = {
            "symbol": meta["symbol"],
            "name": meta["name"],
            "price": round(price, 2),
            "changePct": round(chg, 2),
        }
        summary["asOf"] = last30[-1]["t"] + "T00:00:00Z"

    with open(os.path.join(DATA_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=False)
        f.write("\n")

    with open(os.path.join(DATA_DIR, "prices_30d.json"), "w", encoding="utf-8") as f:
        json.dump({"updatedAt": updated_at, "series": series}, f, indent=2, sort_keys=False)
        f.write("\n")


if __name__ == "__main__":
    main()

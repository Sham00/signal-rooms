#!/usr/bin/env python3
"""Fetch Oil & Gas room data from Stooq (no API key).

Why:
- GitHub Actions often struggles with yfinance rate limits / blocking.
- Stooq provides free daily OHLC data for many commodities + ETFs.

Output (used by rooms/oil-gas/index.html):
- data/oil-gas/summary.json
- data/oil-gas/prices_30d.json

Pages-friendly: pure JSON under data/oil-gas/.
"""

from __future__ import annotations

import csv
import json
import os
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "..", "data", "oil-gas")

# Stooq symbols (CSV endpoint)
# Example endpoint: https://stooq.com/q/d/l/?s=cl.f&i=d
SYMBOLS = {
    "wti": {"label": "WTI", "stooq": "cl.f"},
    "brent": {"label": "Brent", "stooq": "brn.f"},
    "natgas": {"label": "Nat Gas", "stooq": "ng.f"},
    "xle": {"label": "XLE", "stooq": "xle.us"},
}


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stooq_csv_url(symbol: str) -> str:
    # Add a harmless cache-buster; Stooq sometimes serves empty bodies.
    return f"https://stooq.com/q/d/l/?s={symbol}&i=d&_={int(datetime.now(timezone.utc).timestamp())}"


@dataclass
class Point:
    date: str
    close: float


def fetch_stooq_daily_closes(symbol: str, limit: int = 400) -> List[Point]:
    """Fetch daily closes from Stooq.

    NOTE: Stooq sometimes returns HTTP 200 with an "error.csv" attachment or
    other non-CSV bodies when it doesn't like automated traffic. We treat that
    as a soft failure and return [].
    """

    url = stooq_csv_url(symbol)
    try:
        req = urllib.request.Request(
            url,
            headers={
                # Stooq may return empty bodies or policy text to default python/curl UAs.
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
                "Accept": "text/csv,text/plain,*/*",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            cd = (resp.headers.get("Content-Disposition") or "").lower()
            ct = (resp.headers.get("Content-Type") or "").lower()
    except Exception as e:
        print(f"  ERROR fetching {symbol}: {e}")
        return []

    text = (body or "").strip()
    if not text:
        print(f"  WARN {symbol}: empty response")
        return []

    low = text.lower()

    # Common Stooq anti-bot responses.
    if "filename=error.csv" in cd or low.startswith("error"):
        print(f"  WARN {symbol}: stooq returned error.csv")
        return []
    if "write to www@stooq.com" in low:
        print(f"  WARN {symbol}: stooq blocked automated downloads")
        return []

    # Validate this looks like Stooq OHLC CSV.
    if "date," not in low.splitlines()[0]:
        print(f"  WARN {symbol}: unexpected content-type/body (ct={ct})")
        return []

    rows = list(csv.DictReader(text.splitlines()))
    out: List[Point] = []
    for r in rows:
        d = (r.get("Date") or "").strip()
        c = (r.get("Close") or "").strip()
        if not d or not c:
            continue
        try:
            cv = float(c)
        except ValueError:
            continue
        out.append(Point(date=d, close=cv))

    return out[-limit:]


def pct_change(new: float, old: float) -> Optional[float]:
    if old == 0:
        return None
    return round((new - old) / old * 100.0, 2)


def write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main() -> None:
    print("=== fetch_oil_gas_stooq.py ===")

    updated_at = now_utc_iso()
    series_out: Dict[str, List[Dict[str, float]]] = {}
    latest_out: Dict[str, Dict] = {}

    for key, meta in SYMBOLS.items():
        sym = meta["stooq"]
        print(f"  fetching {key} ({sym})...")
        pts = fetch_stooq_daily_closes(sym, limit=120)
        if not pts:
            continue

        tail = pts[-30:]
        series_out[key] = [{"date": p.date, "close": round(p.close, 4)} for p in tail]

        last = pts[-1].close
        prev = pts[-2].close if len(pts) >= 2 else pts[-1].close
        latest_out[key] = {
            "label": meta["label"],
            "stooq": sym,
            "asOf": pts[-1].date,
            "close": round(last, 4),
            "prevClose": round(prev, 4),
            "changePct": pct_change(last, prev),
        }

    summary = {
        "asOf": max((v.get("asOf") for v in latest_out.values() if v.get("asOf")), default=None),
        "updatedAt": updated_at,
        "source": "stooq",
        "latest": latest_out,
    }
    prices_30d = {
        "updatedAt": updated_at,
        "series": series_out,
    }

    write_json(os.path.join(DATA_DIR, "summary.json"), summary)
    write_json(os.path.join(DATA_DIR, "prices_30d.json"), prices_30d)
    print("  wrote summary.json + prices_30d.json")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fetch Mortgage & Housing room data via yfinance (+ FRED if key available)."""
import json, os, time
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "..", "rooms", "housing", "data")

STOCKS = {
    "LEN": "Lennar",
    "DHI": "D.R. Horton",
    "TOL": "Toll Brothers",
    "PHM": "PulteGroup",
}
ETFS = {
    "ITB": "iShares Home Construction ETF",
    "XHB": "SPDR Homebuilders ETF",
    "VNQ": "Vanguard Real Estate ETF",
}
HISTORY_TICKERS = ["ITB", "XHB", "LEN"]


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  wrote {filename}")


def fetch_quote(ticker):
    import yfinance as yf
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")
        if hist.empty:
            return None
        closes = hist["Close"].dropna()
        current = float(closes.iloc[-1])
        prev_close = float(closes.iloc[-2]) if len(closes) > 1 else current
        change_pct = round((current - prev_close) / prev_close * 100, 2)

        today_year = datetime.now().year
        ytd_data = closes[closes.index.year == today_year]
        if not ytd_data.empty:
            ytd_pct = round((current - float(ytd_data.iloc[0])) / float(ytd_data.iloc[0]) * 100, 2)
        else:
            ytd_pct = 0.0

        return {
            "price":      round(current, 2),
            "prev_close": round(prev_close, 2),
            "change_pct": change_pct,
            "ytd_pct":    ytd_pct,
        }
    except Exception as e:
        print(f"  ERROR {ticker}: {e}")
        return None


def fetch_history(ticker):
    import yfinance as yf
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")
        if hist.empty:
            return []
        closes = hist["Close"].dropna()
        return [
            {"date": idx.strftime("%Y-%m-%d"), "close": round(float(val), 2)}
            for idx, val in closes.items()
        ]
    except Exception as e:
        print(f"  ERROR history {ticker}: {e}")
        return []


def fetch_mortgage_rates():
    """Fetch 30yr and 15yr fixed mortgage rates from FRED.

    Requires FRED_API_KEY environment variable.
    Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html
    """
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("  FRED_API_KEY not set — skipping mortgage rates")
        return None, None

    import requests

    def get_series(series_id):
        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}&api_key={api_key}&file_type=json"
            f"&sort_order=desc&limit=1"
        )
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            obs = r.json().get("observations", [])
            if obs and obs[0]["value"] != ".":
                return float(obs[0]["value"])
        except Exception as e:
            print(f"  FRED error for {series_id}: {e}")
        return None

    rate_30y = get_series("MORTGAGE30US")
    rate_15y = get_series("MORTGAGE15US")
    return rate_30y, rate_15y


def main():
    print("=== fetch_housing.py ===")

    stocks_out = {}
    for ticker, name in STOCKS.items():
        print(f"  fetching {ticker}...")
        q = fetch_quote(ticker)
        if q:
            stocks_out[ticker] = {"name": name, **q}
        time.sleep(0.3)

    etfs_out = {}
    for ticker, name in ETFS.items():
        print(f"  fetching {ticker}...")
        q = fetch_quote(ticker)
        if q:
            etfs_out[ticker] = {"name": name, **q}
        time.sleep(0.3)

    print("  fetching mortgage rates...")
    rate_30y, rate_15y = fetch_mortgage_rates()

    write_json("prices.json", {
        "last_updated":       now_utc(),
        "mortgage_rate_30y":  rate_30y,
        "mortgage_rate_15y":  rate_15y,
        "stocks":             stocks_out,
        "etfs":               etfs_out,
    })

    history_out = {}
    for ticker in HISTORY_TICKERS:
        print(f"  fetching history {ticker}...")
        history_out[ticker] = fetch_history(ticker)
        time.sleep(0.3)

    write_json("history.json", {
        "last_updated": now_utc(),
        "tickers": history_out,
    })

    print("  done.")


if __name__ == "__main__":
    main()

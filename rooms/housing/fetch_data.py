#!/usr/bin/env python3
"""Housing Room — Static Data Fetcher
Fetches 30Y mortgage rate and 10Y Treasury from FRED CSV (no API key required).
Writes to data/housing/ at repo root.

Usage:
    python rooms/housing/fetch_data.py
    # or from within rooms/housing/:
    python fetch_data.py
"""
import csv, io, json, os, time
from datetime import datetime, timezone, timedelta

import requests

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, '..', '..')
DATA_DIR = os.path.join(ROOT, 'data', 'housing')

HEADERS = {"User-Agent": "signal-rooms-fetcher/1.0 (public data; github.com/sham00/signal-rooms)"}


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  wrote {filename}")


def fetch_fred_csv(series_id):
    """Fetch a FRED series via the public CSV endpoint (no API key needed)."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    r = requests.get(url, timeout=25, headers=HEADERS)
    r.raise_for_status()
    rows = []
    reader = csv.reader(io.StringIO(r.text))
    header = next(reader, None)  # skip header row
    for row in reader:
        if len(row) < 2:
            continue
        date_str, val_str = row[0].strip(), row[1].strip()
        if val_str in ('.', '', 'NA'):
            continue
        try:
            rows.append({'date': date_str, 'value': float(val_str)})
        except ValueError:
            pass
    return rows


def monthly_payment(principal, annual_rate_pct, n=360):
    """Fixed-rate mortgage P&I monthly payment."""
    r = annual_rate_pct / 100.0 / 12.0
    if r == 0:
        return round(principal / n, 2)
    return round(principal * r * (1 + r) ** n / ((1 + r) ** n - 1), 2)


def filter_1y(rows):
    """Keep only rows within the last ~13 months."""
    cutoff = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
    filtered = [r for r in rows if r['date'] >= cutoff]
    return filtered if filtered else rows[-80:]


def main():
    print("=== rooms/housing/fetch_data.py ===")

    # ── MORTGAGE30US (weekly) ─────────────────────────────────────────────────
    print("  fetching MORTGAGE30US ...")
    m30_all = fetch_fred_csv('MORTGAGE30US')
    m30_1y = filter_1y(m30_all)
    time.sleep(0.5)

    m30_latest   = m30_1y[-1]  if m30_1y              else None
    m30_1w_ago   = m30_1y[-2]  if len(m30_1y) >= 2    else None
    m30_4w_ago   = m30_1y[-5]  if len(m30_1y) >= 5    else None
    m30_52w_ago  = m30_1y[0]   if m30_1y              else None

    # ── DGS10 (daily) ────────────────────────────────────────────────────────
    print("  fetching DGS10 ...")
    dgs10_all = fetch_fred_csv('DGS10')
    dgs10_1y = filter_1y(dgs10_all)
    time.sleep(0.5)

    dgs10_latest = dgs10_1y[-1] if dgs10_1y              else None
    dgs10_1d_ago = dgs10_1y[-2] if len(dgs10_1y) >= 2   else None

    # ── MSPUS (quarterly median sale price) ──────────────────────────────────
    print("  fetching MSPUS ...")
    mspus_latest = None
    try:
        mspus_all = fetch_fred_csv('MSPUS')
        mspus_latest = mspus_all[-1] if mspus_all else None
    except Exception as e:
        print(f"  MSPUS warning: {e}")
    time.sleep(0.5)

    # ── Spread series: align weekly mortgage to daily treasury ───────────────
    dgs10_map = {r['date']: r['value'] for r in dgs10_1y}

    spread_series = []
    for row in m30_1y:
        t_val = dgs10_map.get(row['date'])
        if t_val is None:
            # look up to ±5 business days around the mortgage date
            base_dt = datetime.strptime(row['date'], '%Y-%m-%d')
            for delta in range(-5, 6):
                d = (base_dt + timedelta(days=delta)).strftime('%Y-%m-%d')
                if d in dgs10_map:
                    t_val = dgs10_map[d]
                    break
        if t_val is not None:
            spread_series.append({
                'date':     row['date'],
                'spread':   round(row['value'] - t_val, 3),
                'mortgage': row['value'],
                'treasury': t_val,
            })

    current_spread = spread_series[-1]['spread']  if spread_series else None
    avg_spread_1y  = (
        round(sum(r['spread'] for r in spread_series) / len(spread_series), 3)
        if spread_series else None
    )

    # ── Affordability proxy ───────────────────────────────────────────────────
    home_price = mspus_latest['value'] if mspus_latest else 416000
    loan       = round(home_price * 0.80)
    rate_pct   = m30_latest['value'] if m30_latest else 6.5
    mp         = monthly_payment(loan, rate_pct)

    # ── rates.json ────────────────────────────────────────────────────────────
    rates_out = {
        'last_updated': now_utc(),
        'mortgage_30y': {
            'rate':       m30_latest['value'] if m30_latest else None,
            'date':       m30_latest['date']  if m30_latest else None,
            'change_1w':  round(m30_latest['value'] - m30_1w_ago['value'],  3) if m30_latest and m30_1w_ago  else None,
            'change_4w':  round(m30_latest['value'] - m30_4w_ago['value'],  3) if m30_latest and m30_4w_ago  else None,
            'change_52w': round(m30_latest['value'] - m30_52w_ago['value'], 3) if m30_latest and m30_52w_ago else None,
        },
        'treasury_10y': {
            'rate':      dgs10_latest['value'] if dgs10_latest else None,
            'date':      dgs10_latest['date']  if dgs10_latest else None,
            'change_1d': round(dgs10_latest['value'] - dgs10_1d_ago['value'], 3) if dgs10_latest and dgs10_1d_ago else None,
        },
        'spread': {
            'current': current_spread,
            'avg_1y':  avg_spread_1y,
            'vs_avg':  round(current_spread - avg_spread_1y, 3) if (current_spread is not None and avg_spread_1y is not None) else None,
        },
        'affordability': {
            'home_price_est':  round(home_price),
            'down_pct':        20,
            'loan_amount':     loan,
            'monthly_payment': mp,
            'rate_used':       rate_pct,
            'note':            f"Est. P&I on ${loan:,} @ {rate_pct}%",
            'mspus_date':      mspus_latest['date'] if mspus_latest else 'estimated',
        },
    }
    write_json('rates.json', rates_out)

    # ── history.json ──────────────────────────────────────────────────────────
    history_out = {
        'last_updated': now_utc(),
        'mortgage_30y': [{'date': r['date'], 'rate': r['value']} for r in m30_1y],
        'treasury_10y': [{'date': r['date'], 'rate': r['value']} for r in dgs10_1y],
        'spread':       spread_series,
    }
    write_json('history.json', history_out)

    print("  done.")


if __name__ == '__main__':
    main()

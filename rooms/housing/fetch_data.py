#!/usr/bin/env python3
"""Housing Room — Static Data Fetcher

Fetches 30Y mortgage rate and 10Y Treasury from FRED's public CSV endpoint
(no API key required). Writes JSON under data/housing/ for GitHub Pages.

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


def _check_runtime():
    # Don't hard-fail on older interpreters; just warn.
    if (os.sys.version_info.major, os.sys.version_info.minor) < (3, 9):
        print(
            "[warn] Python 3.9+ recommended. If you hit SSL/urllib3 warnings on macOS, "
            "run with the repo venv: .venv/bin/python rooms/housing/fetch_data.py"
        )


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"  wrote {filename}")


def write_text(filename, text):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"  wrote {filename}")


def _to_float(v):
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _parse_yyyy_mm_dd(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _compute_change(latest_row, prior_row):
    """Compute latest - prior, returning None if inputs missing."""
    if not latest_row or not prior_row:
        return None
    a = latest_row.get('value')
    b = prior_row.get('value')
    if a is None or b is None:
        return None
    return round(a - b, 3)


def _as_pct(v, *, max_reasonable=40.0):
    """Normalize a numeric to a percent.

    FRED series are typically already in percent (e.g., 4.25), but occasionally
    data can arrive as a fraction (e.g., 0.0425). This keeps the site resilient
    against upstream/unit mistakes.
    """
    x = _to_float(v)
    if x is None:
        return None
    if 0 < x < 1:
        x = x * 100.0
    # guard against absurd values (bad parse / unit error)
    if abs(x) > max_reasonable:
        return None
    return x


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


def find_prior_row(rows, latest_date_str, days_back):
    """Find the closest row at or before (latest_date - days_back).

    More robust than fixed index offsets for weekly series.
    """
    latest_dt = _parse_yyyy_mm_dd(latest_date_str)
    if not latest_dt:
        return None
    target = latest_dt - timedelta(days=days_back)

    best = None
    best_dt = None
    for r in rows:
        dt = _parse_yyyy_mm_dd(r.get('date'))
        if not dt or dt > latest_dt:
            continue
        if dt <= target and (best_dt is None or dt > best_dt):
            best = r
            best_dt = dt

    # If no row is old enough (rare), fall back to the last row before latest.
    if best is None:
        for r in reversed(rows):
            dt = _parse_yyyy_mm_dd(r.get('date'))
            if dt and dt < latest_dt:
                return r
    return best


def main():
    print("=== rooms/housing/fetch_data.py ===")

    _check_runtime()

    # ── MORTGAGE30US (weekly) ─────────────────────────────────────────────────
    print("  fetching MORTGAGE30US ...")
    m30_all = fetch_fred_csv('MORTGAGE30US')
    m30_1y = filter_1y(m30_all)
    time.sleep(0.5)

    m30_latest   = m30_1y[-1]  if m30_1y else None
    m30_1w_ago   = find_prior_row(m30_1y, m30_latest['date'], 7)   if m30_latest else None
    m30_4w_ago   = find_prior_row(m30_1y, m30_latest['date'], 28)  if m30_latest else None
    m30_52w_ago  = find_prior_row(m30_1y, m30_latest['date'], 364) if m30_latest else None

    # normalize to percent defensively
    if m30_latest:
        m30_latest['value'] = _as_pct(m30_latest.get('value'), max_reasonable=25.0)
    if m30_1w_ago:
        m30_1w_ago['value'] = _as_pct(m30_1w_ago.get('value'), max_reasonable=25.0)
    if m30_4w_ago:
        m30_4w_ago['value'] = _as_pct(m30_4w_ago.get('value'), max_reasonable=25.0)
    if m30_52w_ago:
        m30_52w_ago['value'] = _as_pct(m30_52w_ago.get('value'), max_reasonable=25.0)

    # ── DGS10 (daily) ────────────────────────────────────────────────────────
    print("  fetching DGS10 ...")
    dgs10_all = fetch_fred_csv('DGS10')
    dgs10_1y = filter_1y(dgs10_all)
    time.sleep(0.5)

    dgs10_latest = dgs10_1y[-1] if dgs10_1y else None
    dgs10_1d_ago = find_prior_row(dgs10_1y, dgs10_latest['date'], 1) if dgs10_latest else None

    # normalize to percent defensively
    if dgs10_latest:
        dgs10_latest['value'] = _as_pct(dgs10_latest.get('value'), max_reasonable=25.0)
    if dgs10_1d_ago:
        dgs10_1d_ago['value'] = _as_pct(dgs10_1d_ago.get('value'), max_reasonable=25.0)

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
    # apply normalization to all treasury rows used in spread alignment
    for r in dgs10_1y:
        r['value'] = _as_pct(r.get('value'), max_reasonable=25.0)

    dgs10_map = {r['date']: r['value'] for r in dgs10_1y if r.get('value') is not None}

    spread_series = []
    for row in m30_1y:
        row['value'] = _as_pct(row.get('value'), max_reasonable=25.0)
        if row.get('value') is None:
            continue
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
    rate_pct   = m30_latest['value'] if (m30_latest and m30_latest.get('value') is not None) else 6.5
    mp         = monthly_payment(loan, rate_pct)

    # ── rates.json ────────────────────────────────────────────────────────────
    rates_out = {
        'last_updated': now_utc(),
        'mortgage_30y': {
            'rate':       m30_latest['value'] if m30_latest else None,
            'date':       m30_latest['date']  if m30_latest else None,
            'change_1w':  _compute_change(m30_latest, m30_1w_ago),
            'change_4w':  _compute_change(m30_latest, m30_4w_ago),
            'change_52w': _compute_change(m30_latest, m30_52w_ago),
        },
        'treasury_10y': {
            'rate':      dgs10_latest['value'] if dgs10_latest else None,
            'date':      dgs10_latest['date']  if dgs10_latest else None,
            'change_1d': _compute_change(dgs10_latest, dgs10_1d_ago),
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

    # ── sources.txt (human-readable provenance for the UI) ───────────────────
    sources_txt = """Housing room data sources (auto-generated)

Series (FRED):
- MORTGAGE30US — 30-Year Fixed Rate Mortgage Average in the United States (weekly)
- DGS10 — Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity (daily)
- MSPUS — Median Sales Price of Houses Sold for the United States (quarterly)

Fetch method:
- https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES_ID> (public CSV endpoint; no API key)

Generated by: rooms/housing/fetch_data.py
Last updated (UTC): {updated}
""".format(updated=rates_out.get('last_updated') or now_utc())
    write_text('sources.txt', sources_txt)

    print("  done.")


if __name__ == '__main__':
    main()

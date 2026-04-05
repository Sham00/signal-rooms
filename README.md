# 📡 Signal Rooms

**Living, breathing situation rooms for major markets.**

This repo is the umbrella “hub” that hosts multiple room dashboards (Gold, GPU/AI compute, Oil & Gas, Mortgage/Housing, etc.) under a single site.

## Preview (local)

```bash
cd /Users/roberto/.openclaw/workspace/projects/signal-rooms
python3 -m http.server 8000
```

Then open:
- http://localhost:8000/ (hub)
- http://localhost:8000/rooms/gold/ (gold room)

## Rooms

- **Gold**: `rooms/gold/` (migrated from the original `gold-situation-room`)
- **GPU / AI Compute**: `rooms/gpu/` (stub)
- **Oil & Gas**: `rooms/oil-gas/` (stub)
- **Mortgage & Housing**: `rooms/housing/` (stub)

---

## Gold Room — What You Get

| Section | What It Shows |
|---|---|
| **Live Spot Price** | COMEX XAU/USD, YTD performance, ATH distance, price in 8 currencies |
| **Market Signal** | Composite bull/bear score from 5 factors — RSI, real yields, DXY, ETF flows, COT |
| **Key Ratios** | Gold/Silver, Gold/Oil, Gold/S&P500, Gold/BTC, Gold/Copper — with 10-year percentiles |
| **Central Bank Tracker** | 20 central banks tracked — reserves, monthly changes, buy/sell/sell-watch status + live CB news feed |
| **Market Alerts** | Auto-detected events: CB selling, large ETF flows, backwardation, lease rate spikes |
| **ETF Flows** | GLD, IAU, PHYS, BAR, SGOL — price, estimated holdings, daily flow direction |
| **COT Positioning** | CFTC managed money longs/shorts/net — with 5-year percentile and futures curve state |
| **COMEX Vault** | Registered vs eligible inventory, cover ratio |
| **Gold Lease Rate** | 1M/3M/6M/12M term structure |
| **News Feed** | Hourly headlines from Kitco, BullionVault, Reuters, Mining.com — with sentiment scoring |
| **Macro Context** | Real yields, DXY, CPI, Fed Funds, M2 — dual-axis correlation charts vs gold |
| **Mining Snapshot** | GDX, GDXJ, majors — AISC, margin, production, junior/senior leverage ratio |
| **Crisis Asset Performance** | YTD: Gold vs BTC vs Silver vs Bonds vs USD — rebased to 100 |
| **Historical Context** | 50+ year price history, decade returns, seasonal patterns |

---

## Data Transparency

Every data point is labeled with its source, update frequency, and reliability level. Click **📋 Data Quality** in the dashboard header for the full breakdown.

| Reliability | Meaning |
|---|---|
| 🟢 LIVE | Real-time or same-day data from authoritative sources |
| 🟡 ESTIMATE | Derived, proxied, or lagged data — labeled clearly |
| 📚 ARCHIVAL | Historical/static dataset |
| ∑ CALCULATED | Derived from other data series |

**Key sources:** [yfinance](https://github.com/ranaroussi/yfinance) (prices), [CFTC](https://www.cftc.gov) (COT), [World Gold Council](https://www.gold.org) (CB reserves), RSS feeds (news)

Full methodology: [rooms/gold/docs/data-methodology.md](rooms/gold/docs/data-methodology.md)

---

*Not financial advice. Data has known limitations — see methodology docs.*

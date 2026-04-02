# 🟡 Gold Situation Room

**Live gold market intelligence dashboard** — price, ratios, central bank flows, ETF positioning, COT data, macro context, and mining stocks in one place.

🔗 **Live site:** https://sham00.github.io/gold-situation-room/

---

## What's Inside

| Section | Data | Updates |
|---|---|---|
| **Spot Price** | COMEX GC=F live price, YTD, ATH, multi-currency | Hourly |
| **Market Signal** | Composite bull/bear score from 5 factors (RSI, real yields, DXY, ETF flows, COT) | Hourly |
| **Key Ratios** | Gold/Silver, Gold/Oil, Gold/S&P500, Gold/BTC, Gold/Copper with 10Y percentiles | Daily |
| **Central Bank Tracker** | 20 CBs tracked — reserves, monthly change, buy/sell status with live news | Hourly news / Quarterly reserves |
| **ETF Flows** | GLD, IAU, PHYS, BAR, SGOL — price, tonne estimates, daily flow | Daily |
| **COT Positioning** | CFTC managed money longs/shorts, net percentile vs 5Y range | Weekly |
| **COMEX Vault** | Registered vs eligible inventory, cover ratio | Monthly |
| **Gold Lease Rate** | 1M/3M/6M/12M term structure | Estimate |
| **News Feed** | Real-time headlines with sentiment scoring (Kitco, BullionVault, Reuters) | Hourly |
| **Macro Context** | Real yields, DXY, CPI, Fed Funds, M2 growth — dual-axis vs gold | Daily |
| **Mining Snapshot** | GDX/GDXJ/majors — price, AISC, margin, production, miner leverage | Daily |
| **Crisis Assets** | YTD performance: Gold vs BTC vs Silver vs TLT vs DXY | Daily |
| **Historical Context** | 50+ year price history, decade returns, seasonality | Monthly/Static |

## Data Transparency

All data is labeled with source, update frequency, and reliability. Click **📋 Data Quality** in the header for the full breakdown.

**Key data sources:** yfinance (prices), CFTC (COT), World Gold Council (CB reserves), RSS feeds (news)

**Known limitations:** CB data lags 3-6 months; lease rates are estimates; LBMA fix is COMEX-proxied.

See [docs/data-methodology.md](docs/data-methodology.md) for the complete methodology.

## Tech Stack

- **Static site** — HTML/CSS/JS + Chart.js + Tailwind CDN
- **Data pipeline** — Python (yfinance, feedparser, requests)
- **Hosting** — GitHub Pages
- **Updates** — GitHub Actions (hourly cron)

## Run Locally

```bash
git clone https://github.com/Sham00/gold-situation-room
cd gold-situation-room
pip install -r requirements.txt
python fetch_data.py   # regenerate data/
open index.html        # view in browser
```

## Deploy to GitHub Pages

1. Push to GitHub
2. **Settings > Pages** → Source: `main` branch, `/ (root)`
3. **Settings > Actions > General** → Workflow permissions: Read and write
4. Run **Actions > Fetch Gold Data** once to populate `data/`
5. Live at `https://<username>.github.io/<repo>/`

## Architecture

```
index.html          Static single-page dashboard (reads data/*.json)
fetch_data.py       Python script that fetches all market data
data/*.json         Pre-fetched JSON data files (auto-updated hourly)
docs/               Methodology and data source documentation
.github/workflows/  GitHub Actions workflow for data pipeline
```

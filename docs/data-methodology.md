# Gold Situation Room — Data Sources & Methodology

*Last updated: April 2026 | Version 1.0*

> **Our commitment:** Every data point on this dashboard is labeled with its source, update frequency, and reliability level. We don't hide limitations — a serious investor deserves to know exactly what they're looking at.

---

## Update Schedule

| Section | Updates | Source | Reliability |
|---|---|---|---|
| Gold Spot Price | Every hour (GitHub Actions) | yfinance → COMEX GC=F front-month | ✅ Live |
| Price Charts (1D/5D) | Every hour | yfinance intraday | ✅ Live |
| Price Charts (1M+) | Daily | yfinance daily close | ✅ Live |
| Key Ratios (Gold/Silver, Oil, S&P, BTC, Copper) | Daily | yfinance (SI=F, CL=F, ^GSPC, BTC-USD, HG=F) | ✅ Live |
| LBMA AM/PM Fix | Daily | yfinance GC=F (COMEX proxy — see note) | ⚠️ Estimate |
| Central Bank Reserves | Quarterly (WGC reports) | Hardcoded from World Gold Council Q4 2025 | ⚠️ Quarterly estimate |
| Central Bank News Feed | Every hour | Google News RSS (CB-keyword filtered) | ✅ Live |
| ETF Holdings (GLD, IAU, PHYS) | Daily | yfinance prices + AUM-derived tonne estimate | ✅ Price live / ⚠️ Tonnes estimated |
| COT Positioning | Weekly (Fridays, prior Tuesday data) | CFTC Commitment of Traders disaggregated report | ✅ Live (3-day lag) |
| COMEX Vault Inventory | Monthly | Hardcoded from COMEX vault reports | ⚠️ Monthly estimate |
| Gold Lease Rate | Static estimate | Approximate market estimates (subscription sources required for live) | ⚠️ Estimate |
| News Feed | Every hour | RSS: Kitco, BullionVault, GoldPrice.org, Google News, Mining.com, Reuters, Investing.com | ✅ Live |
| Macro Indicators (Real Yield, DXY, CPI, Fed Funds, M2) | Daily | yfinance (TNX, TIP, DX-Y.NYB) + FRED-proxy estimates | ✅ Live (some lagged) |
| Mining Stocks (GDX, GDXJ, GOLD, NEM, AEM) | Daily | yfinance | ✅ Live |
| Miner AISC & Production | Quarterly | Hardcoded from company Q4 2025 earnings reports | ⚠️ Quarterly estimate |
| Crisis Asset Performance (YTD) | Daily | yfinance (GC=F, BTC-USD, SI=F, TLT, DXY, VIX) | ✅ Live |
| Historical Price (pre-2000) | Static | London PM Fix historical dataset | 📚 Archival |
| Gold Seasonality | Static | Calculated from all available yfinance history | 📚 Calculated |
| Market Alerts | Every hour | Google News RSS + internal signals | ✅ Live |

---

## Important Limitations

### Central Bank Data

Central bank reserve data is published **quarterly** by the World Gold Council and IMF. Monthly changes shown are estimates based on the most recent quarterly report and known buying patterns. **There is typically a 3-6 month lag** between actual transactions and public disclosure.

**Turkey (TCMB):** Known to make large, rapid reserve changes — sold 58 tonnes in a single two-week period in early 2026. Our data reflects the most recent confirmed quarterly figure (613t, Q4 2025).

**Poland (NBP):** As of March 2026, Poland's central bank chief has proposed selling up to $13B in gold reserves to finance defense spending. **No sales have been confirmed.** This is flagged as ⚠️ SELL WATCH.

### LBMA Fix

The LBMA AM/PM Fix is the global benchmark for physical gold contracts. We display an estimate derived from COMEX futures prices as a proxy — not directly from LBMA data (which requires a subscription). The COMEX-LBMA basis is typically $0-5 during normal markets; during stress periods it can diverge significantly.

### COT Data

The CFTC Commitment of Traders report is published every Friday for positions as of the prior Tuesday. This means the data is always **3-4 days stale** by publication. During fast markets, speculative positioning can shift significantly in that window.

### Gold Lease Rate

Live gold lease rates require access to LBMA/GOFO data (subscription-only). The rates displayed are estimates based on publicly available market commentary. For precise lease rate data, see: LBMA.org.uk (subscription).

### ETF Tonne Estimates

ETF gold holdings in tonnes are calculated by dividing the fund's AUM by the current gold price and the fund's stated gold/share ratio. This is a close approximation but may differ slightly from the fund's official daily holdings disclosure.

---

## Data Sources

| Source | What we use it for | Notes |
|---|---|---|
| **yfinance** (Yahoo Finance) | Price, ratios, ETFs, miners, macro | Real-time during market hours; 15-min delay on some instruments |
| **CFTC** (cftc.gov) | COT positioning data | Official government source; published Fridays |
| **World Gold Council** (gold.org) | Central bank reserves baseline | Quarterly reports; most authoritative source for CB data |
| **RSS Feeds** (Kitco, BullionVault, Reuters, etc.) | News headlines | Real-time; sentiment scoring is keyword-based heuristic |
| **Google News RSS** | Central bank intelligence | Filtered by CB keywords; coverage depends on news volume |
| **COMEX vault reports** | Registered/eligible inventory | Monthly compiled data |
| **Company earnings reports** | Miner AISC, production figures | Q4 2025 reports; updated quarterly |

---

## Market Signal Methodology

The composite bull/bear signal is scored on a **-10 to +10 scale** from 5 independent factors:

| Factor | Weight | Bearish | Neutral | Bullish |
|---|---|---|---|---|
| **RSI Momentum** | ±2 | RSI >70 (overbought) | 35-60 | RSI <30 (oversold/bounce) |
| **Real Yields (10Y TIPS)** | ±2 | >2.5% | 0.5-1.5% | Negative |
| **DXY (USD Index)** | ±2 | >108 (strong USD) | 100-104 | <96 (weak USD) |
| **ETF Daily Flows** | ±2 | Heavy outflows >3t | Flat | Strong inflows >3t |
| **COT Net Percentile** | ±1.5 | >85th (crowded long) | 20-65th | <20th (extreme short) |

**Interpretation:** This is a momentum/positioning composite, not a price forecast. A score of +8 means multiple tailwinds are aligned — it does not predict direction. Gold has historically sustained RSI>70 for months during bull runs.

---

## Contango / Backwardation

Gold is almost always in **contango** (futures > spot) — the basis reflects storage and financing costs (~0.2-0.5% annualized). **Backwardation** (spot > futures) is rare and historically significant, indicating:
- Extreme physical demand / supply shortage
- Delivery stress in the futures market
- Short-squeeze potential

The basis chart shows the spread between COMEX front-month and December futures over time. Red shading = backwardation episodes.

---

## GitHub Actions / Update Infrastructure

Data is refreshed automatically via **GitHub Actions** on a schedule:
- **Hourly:** Price, ratios, news, market alerts, ETFs, crisis assets
- **Daily at market close:** Miners, macro, COT (when published)
- **On push:** Full refresh triggered on any code deploy

The dashboard is a **static site** hosted on GitHub Pages. All data is pre-computed and stored as JSON files. There is no backend server — data freshness depends entirely on the GitHub Actions schedule running successfully.

If a data refresh fails (GitHub Actions timeout, API rate limit), the dashboard will display the last successfully fetched data with a staleness indicator.

---

*Questions or data corrections? Open an issue at github.com/Sham00/gold-situation-room*

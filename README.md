# 📡 Signal Rooms

**Living, breathing situation rooms for major markets.**

Live URL: **https://sham00.github.io/signal-rooms/**

This repo is the umbrella hub hosting multiple market dashboards under one site.
Each room is a self-contained static page, data-fetched by GitHub Actions and committed as JSON.

---

## Rooms

| Room | Path | Status | Update Frequency |
|---|---|---|---|
| **🟡 Gold** | `rooms/gold/` | Live | Hourly |
| **🧠 GPU / AI Compute** | `rooms/gpu/` | Live | Hourly |
| **🛢️ Oil & Gas** | `rooms/oil-gas/` | Live | Hourly |
| **🏠 Mortgage & Housing** | `rooms/housing/` | Live | Hourly |

---

## GitHub Pages Setup

The site deploys automatically via `.github/workflows/pages.yml` on every push to `main`.

**One-time setup required in your repo settings:**
1. Go to **Settings → Pages**
2. Under **Build and deployment → Source**, select **GitHub Actions**
3. The next push to `main` will deploy to `https://sham00.github.io/signal-rooms/`

> **Note:** The workflow includes `enablement: true` in the `configure-pages` step, which will attempt to auto-enable Pages via the API on first run. If it fails, complete the manual step above.

All rooms are served from the repo root. Vendor JS (Chart.js, date adapter) lives in `shared/vendor/` and is committed — no build step needed.

---

## Analytics

All pages include an `<!-- ANALYTICS_PLACEHOLDER -->` comment where you insert tracking code.

Optional: you can also wire a small helper so you only set analytics once:
- `shared/analytics.js` reads `window.SR_ANALYTICS` and injects the chosen provider snippet.
- Pages include `<script src=".../shared/analytics.js"></script>` and keep the placeholder as a reminder.

(No keys are committed — you set them via `window.SR_ANALYTICS` or paste the vendor snippet directly.)

### Option A — Google Analytics 4

Replace `<!-- ANALYTICS_PLACEHOLDER -->` in each `index.html` with:
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```
Substitute your measurement ID for `G-XXXXXXXXXX`.

### Option B — Plausible (privacy-first, no cookie banner)

```html
<script defer data-domain="sham00.github.io" src="https://plausible.io/js/script.js"></script>
```

### Option C — Cloudflare Web Analytics (free, no cookie banner)

1. Enable Web Analytics in your Cloudflare dashboard → **Web Analytics → Add a site**
2. Copy the JS snippet (looks like `<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token":"YOUR_TOKEN"}'></script>`)
3. Replace `<!-- ANALYTICS_PLACEHOLDER -->` in each page with that snippet

Pages that need the placeholder replaced:
- `index.html` (hub)
- `rooms/gold/index.html`
- `rooms/gpu/index.html`
- `rooms/oil-gas/index.html`
- `rooms/housing/index.html`

---

## Local Preview

```bash
cd /path/to/signal-rooms
python3 -m http.server 8000
```

Open:
- http://localhost:8000/ — hub
- http://localhost:8000/rooms/gold/ — gold room
- http://localhost:8000/rooms/gpu/ — GPU room

---

## Data & Fetch Scripts

All fetch scripts live in `scripts/`. Each writes JSON to the corresponding `rooms/<room>/data/` directory.

### Fetch everything (one command)

```bash
pip install -r scripts/requirements.txt
bash scripts/fetch_all.sh
```

### Per-room scripts

| Script | Room | What it fetches |
|---|---|---|
| `scripts/fetch_gold.py` | Gold | COMEX price, ETFs, COT, macro, CB reserves, news (via `rooms/gold/fetch_data.py`) |
| `scripts/fetch_gpu.py` | GPU / AI Compute | NVDA, AMD, SMCI, AMAT, ASML, TSM + SOXX, SMH via yfinance |
| `scripts/fetch_oil_gas.py` | Oil & Gas | WTI/Brent/NatGas futures + XOM, CVX, COP, SLB + XLE, OIH via yfinance |
| `scripts/fetch_all.sh` (housing section) | Mortgage & Housing | Mortgage rates + 10Y treasury + derived spread (committed JSON under `data/housing/`) |

### Cron (local machine)

To update all rooms every hour on your local machine:

```bash
# Run: crontab -e  and add this line:
0 * * * * cd /path/to/signal-rooms && bash scripts/fetch_all.sh >> /tmp/signal-rooms-fetch.log 2>&1
```

### FRED API key (optional — mortgage rates)

Set `FRED_API_KEY` to get live 30yr/15yr fixed mortgage rates in the Housing room.
Free key: https://fred.stlouisfed.org/docs/api/api_key.html

```bash
export FRED_API_KEY=your_key_here
bash scripts/fetch_all.sh
```

In GitHub Actions, add `FRED_API_KEY` as a repository secret (Settings → Secrets).

**Key sources:** yfinance (all price data), CFTC (COT via Gold script), World Gold Council (CB reserves), RSS feeds (news), FRED (mortgage rates)

Full Gold methodology: [rooms/gold/docs/data-methodology.md](rooms/gold/docs/data-methodology.md)

---

## Shared Shell (Nav Bar)

`shared/nav.js` + `shared/shell.css` inject a persistent top nav bar into every room.
Each page loads nav.js with a single `<script>` tag:

```html
<!-- In rooms/<name>/index.html -->
<script src="../../shared/nav.js"></script>

<!-- In index.html (hub) -->
<script src="./shared/nav.js"></script>
```

The nav auto-detects which page is active and highlights it.

---

## Data Reliability Labels

| Label | Meaning |
|---|---|
| 🟢 LIVE | Real-time or same-day from authoritative source |
| 🟡 ESTIMATE | Derived, proxied, or lagged — labeled in UI |
| 📚 ARCHIVAL | Historical/static dataset |
| ∑ CALCULATED | Derived from other series |
| ✍️ MANUAL | Human-maintained; updated on best-effort basis |

---

*Not financial advice. Data has known limitations — see each room's methodology docs.*

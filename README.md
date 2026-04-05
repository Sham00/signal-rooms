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
| **🧠 GPU / AI Compute** | `rooms/gpu/` | Live | Daily |
| **🛢️ Oil & Gas** | `rooms/oil-gas/` | Stub | — |
| **🏠 Mortgage & Housing** | `rooms/housing/` | Stub | — |

---

## GitHub Pages Setup

The site deploys automatically via `.github/workflows/pages.yml` on every push to `main`.

**One-time setup required in your repo settings:**
1. Go to **Settings → Pages**
2. Under **Build and deployment → Source**, select **GitHub Actions**
3. The next push to `main` will deploy to `https://sham00.github.io/signal-rooms/`

---

## Analytics

All pages include an `<!-- ANALYTICS_PLACEHOLDER -->` comment where you insert tracking code.

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

Pages that need the placeholder replaced:
- `index.html` (hub)
- `rooms/gold/index.html`
- `rooms/gpu/index.html`
- `rooms/oil-gas/index.html` *(when built)*
- `rooms/housing/index.html` *(when built)*

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

### Gold Room

| File | What it fetches | Schedule |
|---|---|---|
| `rooms/gold/fetch_data.py` | COMEX price, ETFs, COT, macro, CB reserves, news | Hourly |
| `rooms/gold/data/*.json` | 17 JSON files committed to repo | — |

**Manual run:**
```bash
cd rooms/gold && pip install -r requirements.txt && python fetch_data.py
```

**Key sources:** yfinance (prices), CFTC (COT), World Gold Council (CB reserves), RSS feeds (news)

Full methodology: [rooms/gold/docs/data-methodology.md](rooms/gold/docs/data-methodology.md)

### GPU Room

| File | What it fetches | Schedule |
|---|---|---|
| `rooms/gpu/fetch_data.py` | Lambda Labs via public API; manual data for others | Daily |
| `rooms/gpu/data/providers.json` | Provider × GPU pricing | — |
| `rooms/gpu/data/trends.json` | H100 price history (manual dataset) | — |
| `rooms/gpu/data/availability.json` | Availability by GPU model | — |

**Manual run:**
```bash
cd rooms/gpu && pip install -r requirements.txt && python fetch_data.py
```

**Update cycle:**
- Lambda Labs prices refresh from their public API on every run.
- CoreWeave, RunPod, Vast.ai, AWS, GCP, Azure prices are manually maintained in `fetch_data.py` — update the `MANUAL_PROVIDERS` dict when provider pages change.
- `availability.json` is edited manually when availability status changes.

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

"""GPU / AI Compute Room — Static Data Fetcher

Fetches publicly available GPU cloud pricing and writes JSON to data/ directory.

Data sources:
  - Lambda Labs public API  (no auth needed): /api/v1/instance-types
  - Manual dataset for CoreWeave, RunPod, Vast.ai, AWS, GCP, Azure
    (updated here whenever provider pages change)

Run via GitHub Actions daily, or manually:
    cd rooms/gpu && python fetch_data.py
"""

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Lambda Labs public API ────────────────────────────────────────────────────

LAMBDA_API = "https://cloud.lambdalabs.com/api/v1/instance-types"

# Map Lambda instance names → display metadata
LAMBDA_META = {
    "gpu_8x_h100_sxm5_80gb": {"model": "H100 SXM5", "vram_gb": 80, "gpu_count": 8},
    "gpu_1x_h100_sxm5_80gb": {"model": "H100 SXM5", "vram_gb": 80, "gpu_count": 1},
    "gpu_8x_a100_sxm4_40gb": {"model": "A100 SXM4", "vram_gb": 40, "gpu_count": 8},
    "gpu_1x_a100_sxm4_40gb": {"model": "A100 SXM4", "vram_gb": 40, "gpu_count": 1},
    "gpu_8x_a100_80gb_sxm4": {"model": "A100 SXM4", "vram_gb": 80, "gpu_count": 8},
    "gpu_1x_a100_80gb_sxm4": {"model": "A100 SXM4", "vram_gb": 80, "gpu_count": 1},
    "gpu_1x_a10":             {"model": "A10",       "vram_gb": 24, "gpu_count": 1},
    "gpu_1x_rtx6000ada":      {"model": "RTX 6000 Ada", "vram_gb": 48, "gpu_count": 1},
    "gpu_1x_a6000":           {"model": "RTX A6000", "vram_gb": 48, "gpu_count": 1},
    "gpu_8x_h200_sxm5_141gb": {"model": "H200 SXM5", "vram_gb": 141, "gpu_count": 8},
    "gpu_1x_h200_sxm5_141gb": {"model": "H200 SXM5", "vram_gb": 141, "gpu_count": 1},
}


def fetch_lambda_prices():
    """Fetch Lambda Labs instance pricing from their public API."""
    try:
        resp = requests.get(LAMBDA_API, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", {})
    except Exception as exc:
        print(f"  [WARN] Lambda API error: {exc}")
        return []

    gpus = []
    seen_models = set()
    for instance_name, info in data.items():
        meta = LAMBDA_META.get(instance_name)
        if not meta:
            # Try to infer from instance name
            continue
        # price_cents_per_hour → dollars, divide by GPU count for per-GPU price
        price_cents = info.get("instance_type", {}).get("price_cents_per_hour")
        if price_cents is None:
            continue
        price_per_gpu = price_cents / 100 / meta["gpu_count"]
        avail = bool(info.get("regions_with_capacity_available"))
        model_key = (meta["model"], meta["vram_gb"])
        if model_key in seen_models:
            # Keep cheapest
            existing = next((g for g in gpus if g["model"] == meta["model"] and g["vram_gb"] == meta["vram_gb"]), None)
            if existing and price_per_gpu < existing["price_hr"]:
                existing["price_hr"] = round(price_per_gpu, 4)
                existing["available"] = existing["available"] or avail
            continue
        seen_models.add(model_key)
        gpus.append({
            "model":      meta["model"],
            "vram_gb":    meta["vram_gb"],
            "price_hr":   round(price_per_gpu, 4),
            "available":  avail,
            "spot":       False,
        })

    return gpus


# ── Manual datasets (updated here when provider pages change) ─────────────────

MANUAL_PROVIDERS = [
    {
        "id":   "coreweave",
        "name": "CoreWeave",
        "tier": "specialist",
        "url":  "https://www.coreweave.com/gpu-cloud-computing",
        "gpus": [
            {"model": "H100 SXM5", "vram_gb": 80, "price_hr": 2.89, "available": True,  "spot": False},
            {"model": "A100 SXM4", "vram_gb": 80, "price_hr": 2.21, "available": True,  "spot": False},
            {"model": "L40S",      "vram_gb": 48, "price_hr": 1.33, "available": True,  "spot": False},
            {"model": "RTX A6000", "vram_gb": 48, "price_hr": 0.89, "available": True,  "spot": False},
        ],
    },
    {
        "id":   "runpod",
        "name": "RunPod",
        "tier": "specialist",
        "url":  "https://www.runpod.io/gpu-instance/pricing",
        "gpus": [
            {"model": "H100 PCIe", "vram_gb": 80, "price_hr": 2.89, "available": True, "spot": False},
            {"model": "A100 SXM4", "vram_gb": 80, "price_hr": 1.89, "available": True, "spot": False},
            {"model": "L40S",      "vram_gb": 48, "price_hr": 0.72, "available": True, "spot": False},
            {"model": "RTX 4090",  "vram_gb": 24, "price_hr": 0.74, "available": True, "spot": False},
        ],
    },
    {
        "id":   "vastai",
        "name": "Vast.ai",
        "tier": "marketplace",
        "url":  "https://vast.ai",
        "note": "Peer-to-peer marketplace. Prices are median spot rates and vary by supply/demand.",
        "gpus": [
            {"model": "H100 SXM5", "vram_gb": 80, "price_hr": 2.15, "available": True, "spot": True},
            {"model": "A100 SXM4", "vram_gb": 80, "price_hr": 1.25, "available": True, "spot": True},
            {"model": "L40S",      "vram_gb": 48, "price_hr": 0.65, "available": True, "spot": True},
            {"model": "RTX 4090",  "vram_gb": 24, "price_hr": 0.48, "available": True, "spot": True},
        ],
    },
    {
        "id":   "aws",
        "name": "AWS",
        "tier": "hyperscaler",
        "url":  "https://aws.amazon.com/ec2/instance-types/p5/",
        "note": "On-demand pricing. Multi-GPU instance cost divided by GPU count.",
        "gpus": [
            {"model": "H100 SXM (p5.48xl ÷ 8)",  "vram_gb": 80, "price_hr": 4.17, "available": True, "spot": False},
            {"model": "A100 40GB (p4d.24xl ÷ 8)", "vram_gb": 40, "price_hr": 4.10, "available": True, "spot": False},
            {"model": "V100 (p3.2xlarge)",         "vram_gb": 16, "price_hr": 3.06, "available": True, "spot": False},
            {"model": "T4 (g4dn.xlarge)",          "vram_gb": 16, "price_hr": 0.53, "available": True, "spot": False},
        ],
    },
    {
        "id":   "gcp",
        "name": "Google Cloud",
        "tier": "hyperscaler",
        "url":  "https://cloud.google.com/compute/gpus-pricing",
        "gpus": [
            {"model": "H100 SXM (A3 High ÷ 8)", "vram_gb": 80, "price_hr": 3.10, "available": True, "spot": False},
            {"model": "A100 80GB (A2 Ultra)",    "vram_gb": 80, "price_hr": 3.67, "available": True, "spot": False},
            {"model": "L4",                      "vram_gb": 24, "price_hr": 0.70, "available": True, "spot": False},
            {"model": "T4",                      "vram_gb": 16, "price_hr": 0.35, "available": True, "spot": False},
        ],
    },
    {
        "id":   "azure",
        "name": "Azure",
        "tier": "hyperscaler",
        "url":  "https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/",
        "gpus": [
            {"model": "H100 NVL (ND H100 v5 ÷ 8)", "vram_gb": 94, "price_hr": 3.60, "available": True, "spot": False},
            {"model": "A100 80GB (NC A100 v4)",     "vram_gb": 80, "price_hr": 3.67, "available": True, "spot": False},
            {"model": "V100 (NC6s v3)",             "vram_gb": 16, "price_hr": 0.90, "available": True, "spot": False},
        ],
    },
]


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    providers_out = []

    # 1. Lambda Labs (live API)
    print("Fetching Lambda Labs prices...")
    lambda_gpus = fetch_lambda_prices()
    if lambda_gpus:
        print(f"  Got {len(lambda_gpus)} Lambda GPU SKUs from API")
        providers_out.append({
            "id":   "lambda",
            "name": "Lambda Labs",
            "tier": "specialist",
            "url":  "https://lambdalabs.com/service/gpu-cloud",
            "gpus": sorted(lambda_gpus, key=lambda g: -g["vram_gb"]),
        })
    else:
        # Fall back to last committed data
        print("  Lambda API unavailable — loading existing data")
        try:
            existing = json.loads((DATA_DIR / "providers.json").read_text())
            lambda_existing = next((p for p in existing["providers"] if p["id"] == "lambda"), None)
            if lambda_existing:
                providers_out.append(lambda_existing)
        except Exception:
            print("  [WARN] No existing Lambda data to fall back to")

    # 2. Manual providers
    providers_out.extend(MANUAL_PROVIDERS)

    # Write providers.json
    out = {
        "last_updated": NOW,
        "note": "On-demand spot prices in USD per GPU per hour. Lambda prices via public API; others are manually maintained from provider websites.",
        "providers": providers_out,
    }
    (DATA_DIR / "providers.json").write_text(json.dumps(out, indent=2))
    print(f"Wrote providers.json ({len(providers_out)} providers)")

    # Update last_updated in trends.json (keep existing trend data)
    try:
        trends = json.loads((DATA_DIR / "trends.json").read_text())
        trends["last_updated"] = NOW
        # Append new H100 point if Lambda price changed
        if lambda_gpus:
            h100 = next((g for g in lambda_gpus if "H100" in g["model"]), None)
            if h100:
                last = trends["h100_sxm_lambda"][-1] if trends["h100_sxm_lambda"] else None
                today = NOW[:10]  # YYYY-MM-DD
                if last and last["date"] != today:
                    if abs(h100["price_hr"] - last["price_hr"]) > 0.005:
                        trends["h100_sxm_lambda"].append({
                            "date": today,
                            "price_hr": h100["price_hr"],
                            "note": "Auto-updated by fetch_data.py",
                        })
                        print(f"  Appended new H100 trend point: {today} @ ${h100['price_hr']}")
        (DATA_DIR / "trends.json").write_text(json.dumps(trends, indent=2))
        print("Updated trends.json")
    except Exception as exc:
        print(f"  [WARN] trends.json update failed: {exc}")

    # Update last_updated in availability.json
    try:
        avail = json.loads((DATA_DIR / "availability.json").read_text())
        avail["last_updated"] = NOW
        (DATA_DIR / "availability.json").write_text(json.dumps(avail, indent=2))
        print("Updated availability.json")
    except Exception as exc:
        print(f"  [WARN] availability.json update failed: {exc}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise

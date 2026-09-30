"""honeypot.is v2 (gratis, tanpa key) untuk chain EVM.

Sumber kedua setelah GoPlus. Butuh pair address agar cakupan maksimal.
"pair not found" = pair tak tercover -> {} (fail-open, proteksi lain tetap jalan).
"""
from __future__ import annotations

CHAIN_IDS = {"eth": 1, "bsc": 56, "base": 8453}


def fetch_raw(chain: str, ca: str, pair: str = "", timeout: int = 15) -> dict | None:
    cid = CHAIN_IDS.get((chain or "").lower())
    if not cid or not ca:
        return None
    try:
        import requests
    except Exception:
        return None
    params = {"address": ca, "chainID": cid}
    if pair:
        params["pair"] = pair
    try:
        r = requests.get("https://api.honeypot.is/v2/IsHoneypot", params=params,
                         timeout=timeout, headers={"User-Agent": "degen-scout/1.0"})
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def _num(x) -> float:
    try:
        v = float(x or 0)
        return v * 100.0 if 0 < v <= 1 else max(v, 0.0)
    except Exception:
        return 0.0


def to_flags(raw: dict | None) -> dict:
    """Pure function (mudah dites)."""
    if not isinstance(raw, dict):
        return {}
    hr = raw.get("honeypotResult") or {}
    sim = raw.get("simulationResult") or {}
    summ = raw.get("summary") or {}
    honey = hr.get("isHoneypot") is True
    risk = str(summ.get("risk") or "").lower()
    return {
        "honeypot": honey or risk in ("high", "severe"),
        "buy_tax": _num(sim.get("buyTax", hr.get("buyTax"))),
        "sell_tax": _num(sim.get("sellTax", hr.get("sellTax"))),
        "risk": risk or None,
    }

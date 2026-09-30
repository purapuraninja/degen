"""GoPlus token security (gratis, tanpa API key) untuk chain EVM.

Menutup lubang BSC/Base/ETH: honeypot, mintable, blacklist, proxy,
pausable, tax, holder count. Docs: api.gopluslabs.com.
"""
from __future__ import annotations
import json
import urllib.parse
import urllib.request

API = "https://api.gopluslabs.com/api/v1/token_security/"
CHAIN_IDS = {"eth": "1", "bsc": "56", "base": "8453"}


def fetch_raw(chain: str, ca: str, timeout: int = 15) -> dict | None:
    cid = CHAIN_IDS.get((chain or "").lower())
    if not cid or not ca:
        return None
    url = f"{API}{cid}?contract_addresses={urllib.parse.quote(ca)}"
    req = urllib.request.Request(url, headers={"User-Agent": "degen-scout/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))
    except Exception:
        return None


def to_flags(raw: dict | None, ca: str) -> dict:
    """Pure function (mudah dites). GoPlus pakai '1'/'0' string."""
    if not isinstance(raw, dict):
        return {}
    res = raw.get("result") or {}
    data = res.get((ca or "").lower()) or res.get(ca) or {}
    if not isinstance(data, dict) or not data:
        return {}

    def b(k: str) -> bool:
        return str(data.get(k, "0")) == "1"

    def tax(k: str) -> float:
        try:
            v = float(data.get(k) or 0)
            return v * 100.0 if 0 < v <= 1 else max(v, 0.0)
        except Exception:
            return 0.0

    holders = data.get("holders") or []
    try:
        holder_count = int(data.get("holder_count") or 0) or None
    except Exception:
        holder_count = None
    return {
        "honeypot": b("is_honeypot") or b("cannot_sell_all") or b("cannot_buy"),
        "mint_unlimited": b("is_mintable"),
        "blacklist": b("is_blacklisted") or b("transfer_pausable"),
        "proxy_risky": b("is_proxy"),
        "buy_tax": tax("buy_tax"),
        "sell_tax": tax("sell_tax"),
        "holders": holder_count,
    }

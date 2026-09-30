"""Detail token DexScreener: harga, liq, volume, txns (sumber teknikal + pasar)."""
from __future__ import annotations
import json
import urllib.request
import urllib.parse

def fetch_token_pairs(chain: str, ca: str, timeout: int = 15) -> list[dict]:
    url = f"https://api.dexscreener.com/latest/dex/tokens/{urllib.parse.quote(ca)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "degen-scout/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", "ignore"))
    except Exception as e:
        print(f"[pairs-gagal {ca[:6]}] {e}", flush=True)
        return []
    pairs = data.get("pairs", []) if isinstance(data, dict) else []
    # filter chain bila diminta
    if chain:
        pairs = [p for p in pairs if str(p.get("chainId", "")).lower() == chain]
    return pairs

def best_pair(pairs: list[dict]) -> dict | None:
    if not pairs:
        return None
    return max(pairs, key=lambda p: float((p.get("liquidity") or {}).get("usd") or 0))

def pair_to_market(pair: dict) -> dict:
    liq = pair.get("liquidity") or {}
    fdv = pair.get("fdv") or pair.get("marketCap") or 0
    v = pair.get("volume") or {}
    tx = pair.get("txns") or {}
    buys_5m = ((tx.get("m5") or {})).get("buys", 0)
    sells_5m = ((tx.get("m5") or {}).get("sells", 0))
    return {
        "symbol": pair.get("baseToken", {}).get("symbol", ""),
        "price": float(pair.get("priceUsd") or 0),
        "mcap": float(pair.get("marketCap") or fdv or 0),
        "fdv": float(fdv or 0),
        "liquidity_usd": float(liq.get("usd") or 0),
        "volume_5m": float((v.get("m5") or 0)),
        "volume_1h": float((v.get("h1") or 0)),
        "buys_5m": int(buys_5m or 0),
        "sells_5m": int(sells_5m or 0),
        "price_change_5m": float((pair.get("priceChange") or {}).get("m5") or 0),
        "dex": pair.get("dexId", ""),
        "pair_address": pair.get("pairAddress", ""),
        "pair_created_at": pair.get("pairCreatedAt"),
    }


def pair_age_min(created_ms, now_ms: float | None = None) -> float | None:
    """Umur pair dalam menit. None bila timestamp tak ada (jangan hard-reject)."""
    import time
    try:
        if not created_ms:
            return None
        now = now_ms if now_ms is not None else time.time() * 1000.0
        return max(0.0, (float(now) - float(created_ms)) / 60000.0)
    except Exception:
        return None

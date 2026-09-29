"""Ingestor live: DexScreener boosts + token profiles (gratis, tanpa key).

Sumber panduan: Trending Volume / Top Gainers Ave.ai -> di bot final dipakai
DexScreener sebagai sumber gratis setara (Ave tidak punya API publik).
"""
from __future__ import annotations
import json
import urllib.request

BOOSTS_URL = "https://api.dexscreener.com/token-boosts/top/v1"
PROFILES_URL = "https://api.dexscreener.com/token-profiles/latest/v1"

def _get_json(url: str, timeout: int = 15) -> list | dict:
    req = urllib.request.Request(url, headers={"User-Agent": "degen-scout/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))

def fetch_boosts(chain: str = "solana", limit: int = 20) -> list[dict]:
    """Return list {ca, chain, symbol, ...}. Filter by chain."""
    try:
        data = _get_json(BOOSTS_URL)
    except Exception as e:
        print(f"[ingestor-boosts-gagal] {e}", flush=True)
        return []
    out: list[dict] = []
    for it in data if isinstance(data, list) else []:
        ch = str(it.get("chainId", "")).lower()
        if chain and ch != chain:
            continue
        ca = it.get("tokenAddress", "")
        if not ca:
            continue
        out.append({"ca": ca, "chain": ch or chain,
                    "symbol": it.get("tokenSymbol", ""),
                    "boosted": True, "raw": it})
        if len(out) >= limit:
            break
    return out

def fetch_profiles(chain: str = "solana", limit: int = 20) -> list[dict]:
    try:
        data = _get_json(PROFILES_URL)
    except Exception as e:
        print(f"[ingestor-profiles-gagal] {e}", flush=True)
        return []
    out: list[dict] = []
    for it in data if isinstance(data, list) else []:
        ch = str(it.get("chainId", "")).lower()
        if chain and ch != chain:
            continue
        ca = it.get("tokenAddress", "")
        if not ca:
            continue
        out.append({"ca": ca, "chain": ch or chain,
                    "symbol": it.get("tokenSymbol", ""),
                    "raw": it})
        if len(out) >= limit:
            break
    return out

def fetch_latest_tokens(chain: str = "solana", limit: int = 20) -> list[dict]:
    """Gabungan boosts + profiles, dedup by ca."""
    seen: dict[str, dict] = {}
    for t in fetch_boosts(chain, limit) + fetch_profiles(chain, limit):
        seen.setdefault(f"{t['chain']}:{t['ca']}", t)
    return list(seen.values())[:limit]

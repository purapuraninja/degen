"""Security checker final: RugCheck (Solana, gratis) + heuristik DexScreener.

Panduan Bab 13: honeypot, mint, blacklist/freeze, proxy, tax, LP, ownership.
RugCheck report: https://api.rugcheck.xyz/v1/tokens/<mint>/report
"""
from __future__ import annotations
import json
import urllib.request
import urllib.parse

def fetch_rugcheck(mint: str, timeout: int = 15) -> dict:
    url = f"https://api.rugcheck.xyz/v1/tokens/{urllib.parse.quote(mint)}/report"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "degen-scout/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))
    except Exception as e:
        return {"_error": str(e)[:200]}

def rugcheck_to_flags(rep: dict) -> dict:
    if not isinstance(rep, dict) or rep.get("_error"):
        return {"unknown": True, "error": rep.get("_error", "?")}
    risks = rep.get("risks") or []
    names = " ".join(str(r.get("name", "")) + " " + str(r.get("description", "")) for r in risks).lower()
    token_meta = rep.get("tokenMeta") or {}
    # heuristik keyword RugCheck
    return {
        "honeypot": "honeypot" in names,
        "mint_unlimited": ("mint authority" in names and "still" in names) or bool(rep.get("mintAuthority")),
        "blacklist": "blacklist" in names,
        "can_freeze": bool(rep.get("freezeAuthority")) or "freeze" in names,
        "proxy_risky": "proxy" in names,
        "top1_pct": float((rep.get("topHolders") or [{}])[0].get("pct", 0)) if rep.get("topHolders") else 0.0,
        "risks_count": len(risks),
        "score": rep.get("score"),
    }

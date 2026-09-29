"""Exit manager: TP bertahap + SL + trailing + dust rule (Moonbag / never sell dust)."""
from __future__ import annotations

def build_exit_orders(entry_price: float, cfg: dict) -> list[dict]:
    ex = cfg.get("exit", {})
    tp1 = entry_price * (1 + ex.get("tp1Pct", 50) / 100)
    tp2 = entry_price * (1 + ex.get("tp2Pct", 100) / 100)
    sl = entry_price * (1 - ex.get("slPct", 20) / 100)
    return [
        {"type": "TP1", "price": tp1, "sell_pct": ex.get("tp1SellPct", 25)},
        {"type": "TP2", "price": tp2, "sell_pct": ex.get("tp2SellPct", 25)},
        {"type": "SL", "price": sl, "sell_pct": 100},
    ]

def check_exit(current_price: float, entry_price: float, cfg: dict,
               community_alive: bool = False) -> str:
    """Return HOLD | TP1 | TP2 | SL | DUST_HOLD."""
    ex = cfg.get("exit", {})
    chg = (current_price - entry_price) / max(entry_price, 1e-12) * 100
    if chg >= ex.get("tp2Pct", 100):
        return "TP2"
    if chg >= ex.get("tp1Pct", 50):
        return "TP1"
    if chg <= -float(ex.get("slPct", 20)):
        # CTO-dust rule: jika -80% tapi komunitas hidup -> jangan jual dust
        if chg <= -80 and community_alive:
            return "DUST_HOLD"
        return "SL"
    # trendline jebol disederhanakan: -20% = jual (Sepatah words)
    return "HOLD"

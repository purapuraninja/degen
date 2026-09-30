"""Exit manager: TP bertahap + SL + trailing + dust rule (Moonbag / never sell dust)."""
from __future__ import annotations

def build_exit_orders(entry_price: float, cfg: dict) -> list[dict]:
    """TP1 amankan modal+profit (+100% jual 60% = modal kembali + 20% profit),
    TP2 amankan keuntungan, sisa moonbag dijaga trailing."""
    ex = cfg.get("exit", {})
    tp1 = entry_price * (1 + ex.get("tp1Pct", 100) / 100)
    tp2 = entry_price * (1 + ex.get("tp2Pct", 200) / 100)
    sl = entry_price * (1 - ex.get("slPct", 20) / 100)
    return [
        {"type": "TP1-AMANKAN-MODAL-PROFIT", "price": tp1,
         "sell_pct": ex.get("tp1SellPct", 60)},
        {"type": "TP2-AMANKAN-PROFIT", "price": tp2,
         "sell_pct": ex.get("tp2SellPct", 50)},
        {"type": "TP3-MOONBAG", "price": None, "sell_pct": 0,
         "note": "runner dijaga trailing -50% dari peak"},
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

import sys
sys.path.insert(0, ".")
from src.exit_monitor import decide_exits
from src.positions import apply_fifo

CFG = {"exit": {"tp1Pct": 100, "tp1SellPct": 60, "tp2Pct": 200,
                "tp2SellPct": 50, "slPct": 20, "trailingDropPct": 50}}


def test_tp1():
    acts = decide_exits(1.0, 2.0, 2.0, False, False, CFG)
    assert acts == [("AUTO-TP1", 0.6)], acts


def test_tp1_tp2_sekaligus():
    acts = decide_exits(1.0, 3.0, 3.0, False, False, CFG)
    assert acts == [("AUTO-TP1", 0.6), ("AUTO-TP2", 0.5)], acts


def test_sl():
    assert decide_exits(1.0, 1.0, 0.75, True, False, CFG) == [("AUTO-SL", 1.0)]


def test_trailing():
    # peak 3x, turun >50% -> tutup sisa
    acts = decide_exits(1.0, 3.0, 1.4, True, True, CFG)
    assert acts == [("AUTO-TRAIL", 1.0)], acts
    # turun 30% saja -> tahan
    assert decide_exits(1.0, 3.0, 2.1, True, True, CFG) == []


def test_belum_tp_tahan():
    assert decide_exits(1.0, 1.2, 1.2, False, False, CFG) == []


def test_fifo_realized():
    rows = [
        {"chain": "solana", "ca": "X", "side": "BUY", "amount_sol": 1.0,
         "price": 1.0, "note": "qty=10"},
        {"chain": "solana", "ca": "X", "side": "SELL", "amount_sol": 0.0,
         "price": 2.0, "note": "qty=4"},
    ]
    lots, realized = apply_fifo(rows)
    assert abs(realized - 4.0) < 1e-9, realized
    assert abs(sum(x[0] for x in lots[("solana", "X")]) - 6.0) < 1e-9

"""Decider: threshold BUY/WATCH/SKIP + sizing + exit plan (SOP Bab 6 + Sepatah words)."""

from __future__ import annotations


def decide(score: float, l2: float, cfg: dict) -> str:
    buy_th = cfg.get("scores", {}).get("buyThreshold", 75)
    watch_th = cfg.get("scores", {}).get("watchThreshold", 60)
    min_sm = cfg.get("scores", {}).get("minSmartMoney", 25)
    if score >= buy_th and l2 >= min_sm:
        return "BUY"
    if score >= watch_th:
        return "WATCH"
    return "SKIP"


def position_plan(cfg: dict, chain: str = "solana") -> dict:
    sizing = cfg.get("sizing", {})
    per_play = sizing.get("perPlaySol", 1.0) if chain == "solana" else sizing.get("perPlayBnb", 0.1)
    mark_pct = sizing.get("markPct", 10)
    mark = round(per_play * mark_pct / 100, 4)
    return {"per_play": per_play, "mark_position": mark, "full_entry": round(per_play - mark, 4)}


def exit_plan(cfg: dict) -> dict:
    return cfg.get("exit", {})

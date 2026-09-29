"""Risk manager: kill-switch, daily loss, concurrent limit (Sepatah words: jangan ALL IN)."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class RiskState:
    daily_pnl_sol: float = 0.0
    open_positions: int = 0
    stopped: bool = False

def check_can_buy(state: RiskState, cfg: dict) -> tuple[bool, str]:
    if state.stopped:
        return False, "killed (kill-switch aktif)"
    max_conc = int(cfg.get("sizing", {}).get("maxConcurrent", 5))
    if state.open_positions >= max_conc:
        return False, f"max concurrent {max_conc} tercapai"
    max_loss = float(cfg.get("risk", {}).get("maxDailyLossSol", 0.75))
    if state.daily_pnl_sol <= -abs(max_loss):
        return False, f"daily loss limit {-max_loss} SOL tercapai"
    return True, "ok"

def kill(state: RiskState) -> None:
    state.stopped = True

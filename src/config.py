"""Loader config.yaml (stdlib + pyyaml opsional)."""
from __future__ import annotations
from pathlib import Path

def load_config(path: str | Path = "config.yaml") -> dict:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        # fallback minimal agar bot tetap jalan tanpa pyyaml
        return {
            "chains": ["solana", "bsc"],
            "mode": "DRY_RUN",
            "minLiquidityUSD": {"solana": 8000, "bsc": 5000},
            "maxBuyTaxPct": 10, "maxSellTaxPct": 10,
            "maxTop1HardRejectPct": 15.0, "maxDevPct": 10.0,
            "filters": {"rejectWash": True, "rejectBundledGt20Pct": True},
            "scores": {"buyThreshold": 75, "watchThreshold": 60, "minSmartMoney": 25},
            "sizing": {"maxConcurrent": 5, "perPlaySol": 1.0, "perPlayBnb": 0.1, "markPct": 10},
            "exit": {"tp1Pct": 50, "tp1SellPct": 25, "tp2Pct": 100, "tp2SellPct": 25, "slPct": 20, "trailingStartPct": 200},
            "narrativeTargets": {"default": 3000000},
            "db": {"path": "./degen.db"},
        }

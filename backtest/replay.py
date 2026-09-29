"""Replay sederhana: skor ulang daftar TokenFeatures dari JSON untuk tuning threshold."""
from __future__ import annotations
import json
import sys
sys.path.insert(0, ".")
from src.scorer import TokenFeatures, score_token
from src.config import load_config

def main(path: str, cfg_path: str = "config.yaml") -> None:
    cfg = load_config(cfg_path)
    rows = json.loads(open(path, encoding="utf-8").read())
    for row in rows:
        t = TokenFeatures(**{k: v for k, v in row.items() if k in TokenFeatures.__dataclass_fields__})
        r = score_token(t, cfg)
        print(f"{t.ca} -> {r.decision} {r.score} {r.reasons}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "backtest/sample.json")

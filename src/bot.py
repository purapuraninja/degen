"""Entry bot final. Pakai: python -m src.bot --once | --loop 60"""
from __future__ import annotations
import argparse
import time
from .pipeline import run_once
from .risk import RiskState

def main() -> None:
    ap = argparse.ArgumentParser(description="DEGEN-SCOUT v1 final")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--once", action="store_true", help="1 putaran lalu keluar")
    ap.add_argument("--loop", type=int, default=0, help="ulang tiap N detik (0=sekali)")
    a = ap.parse_args()
    state = RiskState()
    if a.once or a.loop <= 0:
        print(run_once(a.config, a.limit, state), flush=True)
        return
    while True:
        try:
            print(run_once(a.config, a.limit, state), flush=True)
        except KeyboardInterrupt:
            print("STOP oleh user", flush=True)
            break
        except Exception as e:
            print(f"[loop-error] {e}", flush=True)
        time.sleep(a.loop)

if __name__ == "__main__":
    main()

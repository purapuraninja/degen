"""Executor final: DRY_RUN default (aman). Live order butuh kunci + persetujuan.

- DRY_RUN: hanya catat ke DB + print, tanpa dana nyata.
- SEMI_AUTO: cetak instruksi AveSniperBot (@AveSniperBot) untuk approve manual.
- FULL_AUTO: stub Jupiter (Solana) — aktif hanya jika env LIVE_TRADING=1 dan
  private key tersedia. Tanpa itu, otomatis fallback ke DRY_RUN (fail-safe).

SOP panduan Bab 6: cek -> beli -> pantau, slippage auto untuk meme, anti-MEV
untuk dana besar, TP/SL Sleep Order setelah beli.
"""
from __future__ import annotations
import os
import sqlite3
from datetime import datetime, timezone
from ..scorer import TokenFeatures, ScoreResult
from ..decider import position_plan
from ..exit_manager import build_exit_orders

def _log_trade(db_path: str, t: TokenFeatures, side: str, amount: float,
               price: float, note: str) -> None:
    try:
        con = sqlite3.connect(db_path)
        con.execute(
            "INSERT INTO trades(ca,chain,side,amount_sol,price,ts,note) VALUES(?,?,?,?,?,?,?)",
            (t.ca, t.chain, side, amount, price, datetime.now(timezone.utc).isoformat(), note[:500]),
        )
        con.commit()
        con.close()
    except Exception as e:
        print(f"[db-trade-gagal] {e}", flush=True)

def ave_manual_instruction(t: TokenFeatures, amount_sol: float) -> str:
    return (
        f"SEMI_AUTO — eksekusi manual via @AveSniperBot:\n"
        f"1. Set chain: {t.chain}\n"
        f"2. Paste CA: {t.ca}\n"
        f"3. Amount: {amount_sol} ({'SOL' if t.chain=='solana' else 'BNB'})\n"
        f"4. Slippage: AUTO (meme/microcap), Anti-MEV ON untuk dana besar\n"
        f"5. Confirm Buy, lalu set TP/SL (Sleep Order): +50% jual 25%, +100% jual 25%, SL -20%"
    )

def execute_buy(t: TokenFeatures, r: ScoreResult, price: float, cfg: dict) -> dict:
    mode = str(cfg.get("mode", "DRY_RUN")).upper()
    db_path = str(cfg.get("db", {}).get("path", "./degen.db"))
    plan = position_plan(cfg, t.chain)
    amount = plan["per_play"]
    exits = build_exit_orders(price, cfg)
    live_ok = os.getenv("LIVE_TRADING", "0") == "1" and os.getenv("BOT_PRIVATE_KEY", "")

    if mode == "FULL_AUTO" and live_ok:
        # TODO: sambungkan Jupiter/Pancake di sini. Stub tetap catat agar audit jelas.
        _log_trade(db_path, t, "BUY", amount, price,
                   f"LIVE-STUB score={r.score} exits={exits}")
        return {"mode": "FULL_AUTO", "status": "LIVE-STUB",
                "note": "stub live — sambungkan Jupiter/RPC sebelum dana nyata"}
    if mode == "SEMI_AUTO":
        print(ave_manual_instruction(t, amount), flush=True)
        _log_trade(db_path, t, "BUY", amount, price, f"SEMI_AUTO score={r.score}")
        return {"mode": "SEMI_AUTO", "status": "AWAITING_MANUAL", "amount": amount}
    _log_trade(db_path, t, "BUY", amount, price, f"DRY_RUN score={r.score}")
    return {"mode": "DRY_RUN", "status": "PAPER", "amount": amount, "exits": exits}

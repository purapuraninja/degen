"""Paper exit-monitor: auto SELL TP1/TP2/SL/trailing. Tanpa dana nyata.

Aturan (config.yaml -> exit):
- TP1 +tp1Pct%   -> jual tp1SellPct% sisa  (default 50% -> 30%)
- TP2 +tp2Pct%   -> jual tp2SellPct% sisa  (default 100% -> 25%)
- SL  -slPct%    -> tutup semua
- Trailing: aktif setelah TP1 (armed), bila turun trailingDropPct% dari peak
  -> tutup semua sisa. Peak = harga tertinggi sejak entry (persist di DB).

Dipanggil tiap putaran bot (pipeline) + bisa manual: python -m src.exit_monitor
"""
from __future__ import annotations
import sqlite3
import sys

from .positions import apply_fifo, live_market, load_trade_rows, record_sell

STATE_DDL = """CREATE TABLE IF NOT EXISTS paper_state(
  ca TEXT NOT NULL, chain TEXT NOT NULL, peak REAL DEFAULT 0,
  tp1_done INTEGER DEFAULT 0, tp2_done INTEGER DEFAULT 0,
  updated_ts TEXT DEFAULT '',
  PRIMARY KEY (ca, chain))"""


def ensure_state(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.execute(STATE_DDL)
        con.commit()
    finally:
        con.close()


def get_state(db_path: str, chain: str, ca: str) -> dict:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        r = con.execute("select peak,tp1_done,tp2_done from paper_state"
                        " where ca=? and chain=?", (ca, chain)).fetchone()
    finally:
        con.close()
    if not r:
        return {"peak": 0.0, "tp1_done": 0, "tp2_done": 0}
    return {"peak": float(r["peak"] or 0), "tp1_done": int(r["tp1_done"] or 0),
            "tp2_done": int(r["tp2_done"] or 0)}


def set_state(db_path: str, chain: str, ca: str, peak: float,
              tp1_done: int, tp2_done: int) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.execute("INSERT OR REPLACE INTO paper_state(ca,chain,peak,tp1_done,"
                    "tp2_done,updated_ts) VALUES(?,?,?,?,?,datetime('now'))",
                    (ca, chain, peak, tp1_done, tp2_done))
        con.commit()
    finally:
        con.close()


def decide_exits(avg: float, peak: float, cur: float,
                 tp1_done: bool, tp2_done: bool, cfg: dict) -> list[tuple[str, float]]:
    """Pure function (mudah dites). Return [(tag, fraksi_dari_sisa)]."""
    out: list[tuple[str, float]] = []
    if not cur or not avg or cur <= 0 or avg <= 0:
        return out
    ex = cfg.get("exit", {})
    tp1 = float(ex.get("tp1Pct", 50))
    tp2 = float(ex.get("tp2Pct", 100))
    sl = float(ex.get("slPct", 20))
    drop = float(ex.get("trailingDropPct", 50))
    gain = (cur - avg) / avg * 100.0
    if gain <= -sl:
        return [("AUTO-SL", 1.0)]
    if not tp1_done and gain >= tp1:
        out.append(("AUTO-TP1", float(ex.get("tp1SellPct", 30)) / 100.0))
    if not tp2_done and gain >= tp2:
        out.append(("AUTO-TP2", float(ex.get("tp2SellPct", 25)) / 100.0))
    armed = tp1_done or (not tp1_done and gain >= tp1)
    if armed and peak > 0 and (peak - cur) / peak >= drop / 100.0:
        out.append(("AUTO-TRAIL", 1.0))
    return out


def run_exit_check(db_path: str, cfg: dict) -> list[dict]:
    """Cek semua posisi open, eksekusi SELL paper yang terpicu. Return aksi."""
    ensure_state(db_path)
    lots, _ = apply_fifo(load_trade_rows(db_path))
    actions: list[dict] = []
    for (chain, ca), ls in lots.items():
        oq = sum(x[0] for x in ls)
        if oq <= 0:
            continue
        m = live_market(chain, ca)
        cur = (m["price"] if m else None) or 0.0
        if not cur:
            continue
        avg = sum(x[0] * x[1] for x in ls) / oq
        st = get_state(db_path, chain, ca)
        peak = max(st["peak"], cur, avg)
        tp1_done, tp2_done = bool(st["tp1_done"]), bool(st["tp2_done"])
        for tag, frac in decide_exits(avg, peak, cur, tp1_done, tp2_done, cfg):
            q = oq * frac
            if q <= 1e-9:
                continue
            # konsumsi FIFO agar realized ikut benar
            left, nq = q, oq
            li = 0
            while left > 1e-12 and li < len(ls):
                take = min(ls[li][0], left)
                ls[li][0] -= take
                left -= take
                if ls[li][0] <= 1e-12:
                    li += 1
            ls = [x for x in ls if x[0] > 1e-12]
            record_sell(db_path, ca, chain, q, cur, tag)
            oq = sum(x[0] for x in ls)
            if tag == "AUTO-TP1":
                tp1_done = True
            if tag == "AUTO-TP2":
                tp2_done = True
            actions.append({"ca": ca, "chain": chain, "tag": tag,
                            "qty": round(q, 4), "price": cur,
                            "gain_pct": round((cur - avg) / avg * 100, 1)})
            if tag in ("AUTO-SL", "AUTO-TRAIL"):
                break
        set_state(db_path, chain, ca, peak, int(tp1_done), int(tp2_done))
    return actions


if __name__ == "__main__":
    from .config import load_config
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    cfg = load_config(str(root / "config.yaml"))
    db = str(root / cfg.get("db", {}).get("path", "./degen.db"))
    for a in run_exit_check(db, cfg):
        print(a, flush=True)
    print("exit-check selesai", flush=True)

"""Akuntansi posisi paper bersama (FIFO lots). Dipakai dashboard + exit-monitor.

BUY menambah lot [qty, price]. SELL (manual Close / AUTO-TP/SL/TRAIL) menutup
lot FIFO. Sisa lot = posisi open. Semua nilai USD paper, tanpa dana nyata.
"""
from __future__ import annotations
import re
import sqlite3

from .exit_manager import check_exit
from .ingestor.token_detail import fetch_token_pairs, best_pair, pair_to_market


def db_con(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def safe_sym(s: str) -> str:
    return str(s or "?").encode("ascii", "ignore").decode() or "?"


def live_market(chain: str, ca: str) -> dict | None:
    try:
        bp = best_pair(fetch_token_pairs(chain, ca))
        return pair_to_market(bp) if bp else None
    except Exception:
        return None


def buy_qty(note: str | None, amount, price) -> float:
    m = re.search(r"qty=([\d.eE+-]+)", note or "")
    if m:
        try:
            return float(m.group(1))
        except Exception:
            pass
    try:
        return float(amount or 0) / float(price or 0) if price else 0.0
    except Exception:
        return 0.0


def load_trade_rows(db_path: str) -> list:
    try:
        con = db_con(db_path)
        rows = con.execute(
            "select ca,chain,side,amount_sol,price,ts,note from trades order by rowid"
        ).fetchall()
        con.close()
        return rows
    except Exception:
        return []


def apply_fifo(rows: list) -> tuple[dict, float]:
    """Return (lots {(chain,ca): [[qty,price],...]}, realized_usd)."""
    lots: dict[tuple, list] = {}
    realized = 0.0
    for r in rows:
        key = (r["chain"], r["ca"])
        lots.setdefault(key, [])
        if (r["side"] or "").upper() == "BUY":
            q = buy_qty(r["note"], r["amount_sol"], r["price"])
            if q > 0:
                lots[key].append([q, float(r["price"] or 0)])
        else:
            m = re.search(r"qty=([\d.eE+-]+)", r["note"] or "")
            try:
                q = float(m.group(1)) if m else sum(x[0] for x in lots[key])
            except Exception:
                q = sum(x[0] for x in lots[key])
            sp = float(r["price"] or 0)
            left = q
            while left > 1e-12 and lots[key]:
                take = min(lots[key][0][0], left)
                realized += (sp - lots[key][0][1]) * take
                lots[key][0][0] -= take
                left -= take
                if lots[key][0][0] <= 1e-12:
                    lots[key].pop(0)
    return lots, realized


def open_count(db_path: str) -> int:
    """Jumlah posisi open distinct (tanpa fetch live). Untuk risk manager."""
    lots, _ = apply_fifo(load_trade_rows(db_path))
    return sum(1 for ls in lots.values() if sum(x[0] for x in ls) > 0)


def symbol_of(db_path: str, chain: str, ca: str) -> str:
    try:
        con = db_con(db_path)
        r = con.execute("select symbol from tokens where ca=? and chain=?",
                        (ca, chain)).fetchone()
        con.close()
        if r and r["symbol"]:
            return safe_sym(r["symbol"])
    except Exception:
        pass
    return safe_sym(ca[:6])


def record_sell(db_path: str, ca: str, chain: str, qty: float,
                price: float, tag: str) -> None:
    con = db_con(db_path)
    try:
        con.execute(
            "INSERT INTO trades(ca,chain,side,amount_sol,price,ts,note)"
            " VALUES(?,?,?,?,?,datetime('now'),?)",
            (ca, chain, "SELL", 0.0, float(price),
             f"{tag} qty={qty:.4f} @ {price}"))
        con.commit()
    finally:
        con.close()


def build_positions(db_path: str, cfg: dict) -> dict:
    lots, realized = apply_fifo(load_trade_rows(db_path))
    positions = []
    unreal = 0.0
    for (chain, ca), ls in lots.items():
        oq = sum(x[0] for x in ls)
        if oq <= 0:
            continue
        avg = sum(x[0] * x[1] for x in ls) / oq
        m = live_market(chain, ca)
        cur = (m["price"] if m else None) or None
        nilai = oq * cur if cur else None
        pnl = (nilai - oq * avg) if cur else None
        pnl_pct = ((cur - avg) / avg * 100) if (cur and avg) else None
        status = check_exit(cur, avg, cfg) if cur else "UNKNOWN"
        if pnl is not None:
            unreal += pnl
        positions.append({
            "ca": ca, "chain": chain, "symbol": symbol_of(db_path, chain, ca),
            "mcap": m["mcap"] if m else None,
            "liq": m["liquidity_usd"] if m else None,
            "avg_entry": avg, "qty": oq, "cost": oq * avg,
            "price": cur, "nilai": nilai, "pnl": pnl, "pnl_pct": pnl_pct,
            "exit": status,
        })
    positions.sort(key=lambda p: (p["pnl"] is None, -(p["pnl"] or 0)))
    return {"positions": positions,
            "totals": {"unrealized": unreal, "realized": realized,
                       "total": unreal + realized,
                       "open_count": len(positions)}}

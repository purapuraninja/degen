"""Pipeline final: READ (live) -> ANALYZE (scorer) -> DECIDE (winner) -> BUY.

Alur 1 putaran:
1. Ambil kandidat live (DexScreener boosts/profiles).
2. Untuk tiap kandidat: ambil pair terbaik + RugCheck (Solana) -> features -> score.
3. Simpan skor ke DB (tokens).
4. Pilih 1 winner (EV terbesar) -> cek risk -> execute_buy.
"""
from __future__ import annotations
import sqlite3
from .config import load_config
from .notify import notify
from .risk import RiskState, check_can_buy
from .scorer import score_token, pick_winner
from .decider import decide
from .ingestor.dexscreener import fetch_latest_tokens
from .ingestor.token_detail import fetch_token_pairs, best_pair, pair_to_market
from .analyzer.security import fetch_rugcheck, rugcheck_to_flags
from .analyzer.features import build_features
from .executor.buyer import execute_buy

def _save_score(db_path: str, t, r) -> None:
    try:
        con = sqlite3.connect(db_path)
        con.execute(
            "INSERT OR REPLACE INTO tokens(ca,chain,symbol,mcap,liquidity_usd,holders,score,decision,reason)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            (t.ca, t.chain, t.symbol, t.mcap, t.liquidity_usd, t.holders,
             r.score, r.decision, ";".join(r.reasons)[:500]),
        )
        con.commit()
        con.close()
    except Exception as e:
        print(f"[db-score-gagal] {e}", flush=True)

def _safe(s: str) -> str:
    return str(s).encode("ascii", "ignore").decode() or "?"


def run_once(cfg_path: str = "config.yaml", limit: int = 10,
             state: RiskState | None = None) -> dict:
    cfg = load_config(cfg_path)
    state = state or RiskState()
    db_path = str(cfg.get("db", {}).get("path", "./degen.db"))
    scored: list = []
    for chain in cfg.get("chains", ["solana"]):
        cands = fetch_latest_tokens(chain, limit)
        notify(f"[READ] {chain}: {len(cands)} kandidat live")
        for c in cands:
            ca = c["ca"]
            pairs = fetch_token_pairs(chain, ca)
            bp = best_pair(pairs)
            if not bp:
                continue
            market = pair_to_market(bp)
            sec = {"unknown": True}
            if chain == "solana":
                sec = rugcheck_to_flags(fetch_rugcheck(ca))
            t = build_features(ca, chain, market, sec,
                               {"symbol": c.get("symbol", market.get("symbol", ""))})
            r = score_token(t, cfg)
            # sinkronkan decider (redundan tapi eksplisit)
            r.decision = decide(r.score, r.l2, cfg) if not r.reasons[0].startswith("L0") else "SKIP"
            _save_score(db_path, t, r)
            scored.append((t, r))
            sym = _safe(t.symbol or ca[:6])
            print(f"[{r.decision}] {sym} {chain} score={r.score} "
                  f"L1={r.l1} L2={r.l2} L3={r.l3} mcap={t.mcap:.0f} liq={t.liquidity_usd:.0f} "
                  f"{_safe(r.reasons)}", flush=True)
    win = pick_winner(scored, cfg)
    if not win:
        notify("[DECIDE] tidak ada BUY — semua SKIP/WATCH")
        return {"winner": None, "scored": len(scored)}
    t, r, ev = win
    notify(f"[DECIDE] WINNER {_safe(t.symbol or t.ca)} {t.chain} score={r.score} EV={ev} mcap={t.mcap:.0f}")
    ok, why = check_can_buy(state, cfg)
    if not ok:
        notify(f"[RISK-BLOCK] {why}")
        return {"winner": str(t.ca), "blocked": why}
    price = t.mcap / 1e9 if t.mcap > 0 else 0.0  # proksi; executor pakai harga pasar aktual
    res = execute_buy(t, r, price or 1.0, cfg)
    state.open_positions += 1
    notify(f"[BUY] {res}")
    return {"winner": t.ca, "score": r.score, "ev": ev, "exec": res}

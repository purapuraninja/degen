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


def _helius_rescore(ca, chain, market, sec, t, r, cfg):
    """Deep-dive Helius untuk kandidat Solana lolos awal: timpa default
    heuristik dengan observasi on-chain lalu skor ulang. Gagal -> skor awal."""
    if chain != "solana":
        return t, r
    try:
        from .ingestor.helius import load_key, deep_dive
    except Exception:
        return t, r
    key = load_key()
    if not key:
        return t, r
    watch_th = cfg.get("scores", {}).get("watchThreshold", 60)
    if r.score < watch_th and not r.decision == "BUY":
        return t, r
    try:
        obs = deep_dive(ca, key, with_bundle=(r.decision == "BUY"))
    except Exception as e:
        print(f"[helius-gagal {ca[:6]}] {str(e)[:120]}", flush=True)
        return t, r
    if not obs:
        return t, r
    extra = {"symbol": t.symbol, "top1_pct": t.top1_pct,
             "bundle_max_cluster_pct": t.bundle_max_cluster_pct,
             "bundle_cluster_count": t.bundle_cluster_count}
    for k in ("top1_pct", "top10_virgin_ratio", "holders",
              "bundle_max_cluster_pct", "bundle_cluster_count"):
        if k in obs:
            extra[k] = obs[k]
    sec2 = dict(sec)
    if "mint_unlimited" in obs:
        sec2["mint_unlimited"] = obs["mint_unlimited"]
    if "can_freeze" in obs:
        sec2["can_freeze"] = obs["can_freeze"]
    t2 = build_features(ca, chain, market, sec2, extra)
    # pertahankan sinyal sosial/teknikal dari putaran pertama (belum live)
    for f in ("signal_count", "signal_distinct_wallets", "jp_wallet_count",
              "whale_inflow", "kol_tagged_inflow", "mention_per_hour",
              "kol_legit_shill", "cabal_edge", "dex_boost_early",
              "dex_boost_after_pump", "community_healthy", "volume_spike_mult",
              "fomo_top", "dip_state", "at_support", "risk_reward", "narrative"):
        setattr(t2, f, getattr(t, f))
    r2 = score_token(t2, cfg)
    r2.decision = decide(r2.score, r2.l2, cfg) if not r2.reasons[0].startswith("L0") else "SKIP"
    r2.reasons = r2.reasons + ["helius:holder+authority real"]
    print(f"[HELIUS] {t2.symbol or ca[:6]} top1={extra.get('top1_pct')}% "
          f"holders={extra.get('holders', '?')} virgin={extra.get('top10_virgin_ratio', '?')} "
          f"bundle={extra.get('bundle_max_cluster_pct')}% -> {r2.decision} {r2.score}",
          flush=True)
    return t2, r2

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
            if not r.reasons[0].startswith("L0"):
                t, r = _helius_rescore(ca, chain, market, sec, t, r, cfg)
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

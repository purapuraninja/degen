"""Scorer DEGEN-SCOUT v1 — implementasi pipeline §4 PLAN_BOT_DEGEN_AVE.md.

Sumber aturan:
- L0 hard reject: Bab 13 Analysis Tools + Revoke/Mint + Honeypot + LP + GlobalFees wash.
- L1 (30): holder greenflag top1<5%/ideal<4% + bundle BubbleMaps + fee organik (Bab 10 + Bundle + GlobalFees).
- L2 (40): signal 2-5x wallet beda + JP wallet/whale + sosial/KOL/cabal/dexPaid timing (Bab 14 + Signal Monitor + Cabal).
- L3 (30): momentum volume +300%/10mnt + 3 konfirmasi candle + R:R (Bab 10.4 + 3 Candle + Sepatah words).

Tanpa dependensi eksternal (stdlib only) agar bisa dites langsung.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


# ---------------------------------------------------------------- token input
@dataclass
class TokenFeatures:
    ca: str = ""
    chain: str = "solana"          # solana | bsc | base | eth
    symbol: str = ""
    mcap: float = 0.0
    liquidity_usd: float = 0.0
    lp_locked_pct: float = 0.0
    lp_burned: bool = False
    # security (Smart Contract Reader)
    honeypot: bool = False
    cannot_buy: bool = False
    cannot_sell: bool = False
    mint_unlimited: bool = False    # mint authority aktif tanpa supply cap
    blacklist: bool = False
    can_freeze: bool = False
    proxy_risky: bool = False       # proxy + implementation bisa diganti
    buy_tax: float = 0.0
    sell_tax: float = 0.0
    top1_pct: float = 0.0
    dev_pct: float = 0.0
    holders: int = 0
    # distribution
    top10_virgin_ratio: float = 0.0  # 0..1
    holder_growth_15m: int = 0
    bundle_max_cluster_pct: float = 0.0
    bundle_cluster_count: int = 0
    narrative_strength: float = 0.0  # 0..6, untuk threshold adaptif
    # global fees (Solana 0.25%)
    fee_ratio: float = 1.0           # actual/expected; <0.3 wash, 0.7-1.3 organik
    unique_wallets_5m: int = 0
    is_first_second_spike: bool = False
    # smart money
    signal_count: int = 0
    signal_distinct_wallets: bool = True
    jp_wallet_count: int = 0
    whale_inflow: bool = False
    kol_tagged_inflow: bool = False
    virgin_inflow_penalty: bool = False
    # social
    mention_per_hour: int = 0
    kol_legit_shill: bool = False
    kol_dumper_shill: bool = False
    cabal_edge: bool = False         # 2+ KOL co-buy bersamaan
    dex_boost_early: bool = False    # boost di awal + organik
    dex_boost_after_pump: bool = False
    community_healthy: bool = False
    # technical
    volume_spike_mult: float = 1.0
    fomo_top: bool = False           # +100%/5mnt tanpa pullback
    dip_state: str = "none"          # none | dip1 | bounce | dip2_ok | dip2_break
    at_support: bool = False
    risk_reward: float = 0.0
    # bonus/penalti
    cto_revival: bool = False
    pvp_same_ticker_24h: int = 0
    dusting_pattern: bool = False
    narrative: str = "default"
    extra: dict = field(default_factory=dict)


@dataclass
class ScoreResult:
    decision: str                    # BUY | WATCH | SKIP
    score: float
    l1: float = 0.0
    l2: float = 0.0
    l3: float = 0.0
    reasons: list = field(default_factory=list)


# ---------------------------------------------------------------- L0
def l0_reject(t: TokenFeatures, cfg: dict) -> str | None:
    min_liq = cfg.get("minLiquidityUSD", {}).get(t.chain, 8000)
    if t.honeypot or t.cannot_sell or t.cannot_buy:
        return "L0 honeypot/cannot-trade"
    if t.mint_unlimited:
        return "L0 mint-unlimited"
    if t.blacklist or t.can_freeze:
        return "L0 blacklist/freeze"
    if t.proxy_risky:
        return "L0 proxy-risky"
    if t.buy_tax > cfg.get("maxBuyTaxPct", 10) or t.sell_tax > cfg.get("maxSellTaxPct", 10):
        return "L0 tax>10%"
    if t.liquidity_usd < min_liq:
        return "L0 liq<min"
    if t.lp_locked_pct < 70 and not t.lp_burned:
        return "L0 lp-unlocked"
    if t.top1_pct > cfg.get("maxTop1HardRejectPct", 15.0):
        return "L0 top1>15%"
    if t.dev_pct > cfg.get("maxDevPct", 10.0):
        return "L0 dev>10%"
    if t.dusting_pattern:
        return "L0 dusting"
    if cfg.get("filters", {}).get("rejectWash", True) and is_wash(t):
        return "L0 wash-trading"
    if cfg.get("filters", {}).get("rejectBundledGt20Pct", True) and t.bundle_max_cluster_pct > 20:
        return "L0 bundled>20%"
    return None


def is_wash(t: TokenFeatures) -> bool:
    return (t.fee_ratio < 0.3 and t.unique_wallets_5m < 50) or (
        t.is_first_second_spike and t.fee_ratio < 0.5
    )


# ---------------------------------------------------------------- L1 (max 30)
def holder_score(t: TokenFeatures) -> float:
    if t.top1_pct < 4.0:
        s = 10.0
    elif t.top1_pct <= 5.0:
        s = 7.0
    elif t.top1_pct <= 8.0:
        s = 3.0
    else:
        s = 0.0
    if t.top10_virgin_ratio > 0.30:
        s -= 5.0
    if t.holder_growth_15m >= 50:
        s += 1.0
    return max(0.0, min(10.0, s))


def bundle_score(t: TokenFeatures) -> float:
    if t.bundle_max_cluster_pct > 20 or t.bundle_cluster_count > 3:
        return 0.0
    if t.bundle_max_cluster_pct >= 10:
        return 5.0
    return 10.0


def fee_score(t: TokenFeatures) -> float:
    if is_wash(t):
        return 0.0
    if 0.7 <= t.fee_ratio <= 1.3 and t.unique_wallets_5m >= 100:
        return 10.0
    if 0.5 <= t.fee_ratio <= 1.5 and t.unique_wallets_5m >= 50:
        return 6.0
    return 2.0


# ---------------------------------------------------------------- L2 (max 40)
def signal_score(t: TokenFeatures) -> float:
    if t.signal_count <= 0:
        return 0.0
    if 2 <= t.signal_count <= 5 and t.signal_distinct_wallets:
        return 12.0
    if t.signal_count == 1:
        return 4.0
    return 2.0  # >5 tapi wallet sama -> kemungkinan boost bayaran


def wallet_score(t: TokenFeatures) -> float:
    s = min(10.0, t.jp_wallet_count * 5.0)
    if t.whale_inflow:
        s += 2.0
    if t.kol_tagged_inflow:
        s += 2.0
    if t.virgin_inflow_penalty:
        s -= 2.0
    return max(0.0, min(14.0, s))


def social_score(t: TokenFeatures) -> float:
    s = 0.0
    if t.mention_per_hour > 50:
        s += 6.0
    elif t.mention_per_hour >= 10:
        s += 3.0
    if t.kol_legit_shill:
        s += 4.0
    if t.kol_dumper_shill:
        s -= 5.0
    if t.cabal_edge:
        s += 4.0
    if t.dex_boost_early:
        s += 2.0
    if t.dex_boost_after_pump:
        s -= 5.0
    if t.community_healthy:
        s += 2.0
    return max(0.0, min(14.0, s))


# ---------------------------------------------------------------- L3 (max 30)
def momentum_score(t: TokenFeatures) -> float:
    if t.fomo_top:
        return 0.0
    if t.volume_spike_mult >= 3.0:
        return 10.0
    if t.volume_spike_mult >= 2.0:
        return 6.0
    return 2.0


def three_candle_score(t: TokenFeatures) -> float:
    mapping = {
        "dip2_ok": 12.0,
        "bounce": 5.0,   # mark position 10%
        "dip1": 0.0,     # jangan masuk
        "dip2_break": 0.0,
        "none": 3.0,
    }
    s = mapping.get(t.dip_state, 0.0)
    if t.at_support and t.dip_state == "dip2_ok":
        s = 12.0
    if not t.at_support and t.dip_state == "dip2_ok":
        s = 7.0
    return s


def rr_score(t: TokenFeatures) -> float:
    if t.risk_reward >= 3.0:
        return 8.0
    if t.risk_reward >= 2.0:
        return 4.0
    return 0.0


# ---------------------------------------------------------------- gabungan
def score_token(t: TokenFeatures, cfg: dict) -> ScoreResult:
    rej = l0_reject(t, cfg)
    if rej:
        return ScoreResult(decision="SKIP", score=0.0, reasons=[rej])

    l1 = holder_score(t) + bundle_score(t) + fee_score(t)
    l2 = signal_score(t) + wallet_score(t) + social_score(t)
    l3 = momentum_score(t) + three_candle_score(t) + rr_score(t)
    total = l1 + l2 + l3

    reasons: list[str] = []
    if t.cto_revival:
        total += 5.0
        reasons.append("bonus CTO-revival +5")
    if t.pvp_same_ticker_24h > 3:
        total -= 10.0
        reasons.append("penalti PVP -10 (ticker sama >3)")
    total = max(0.0, min(105.0, total))

    buy_th = cfg.get("scores", {}).get("buyThreshold", 75)
    watch_th = cfg.get("scores", {}).get("watchThreshold", 60)
    min_sm = cfg.get("scores", {}).get("minSmartMoney", 25)

    if total >= buy_th and l2 >= min_sm:
        dec = "BUY"
    elif total >= watch_th:
        dec = "WATCH"
    else:
        dec = "SKIP"
    reasons = [f"L1={l1:.0f} L2={l2:.0f} L3={l3:.0f}"] + reasons
    return ScoreResult(decision=dec, score=round(total, 1), l1=round(l1, 1),
                       l2=round(l2, 1), l3=round(l3, 1), reasons=reasons)


def pick_winner(cands: list[tuple[TokenFeatures, ScoreResult]], cfg: dict):
    """Pilih 1 dengan expected profit terbesar: EV = score * log(upside+1) / risk."""
    buys = [(t, r) for t, r in cands if r.decision == "BUY"]
    if not buys:
        return None
    targets = cfg.get("narrativeTargets", {})
    best = None
    best_ev = -1.0
    for t, r in buys:
        target = float(targets.get(t.narrative, targets.get("default", 3_000_000)))
        upside = (target / max(t.mcap, 1.0))
        risk = 1.0 + (t.bundle_max_cluster_pct / 20.0) + (0.5 if t.fomo_top else 0.0)
        ev = r.score * math.log(upside + 1) / risk
        if ev > best_ev:
            best_ev = ev
            best = (t, r, round(ev, 2))
    return best

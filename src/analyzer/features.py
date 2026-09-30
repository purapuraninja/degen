"""Build TokenFeatures dari data live (DexScreener + RugCheck) + sinyal opsional.

Ini jembatan READ -> ANALYZE. Kolom yang tidak tersedia live diberi default
konservatif (fail-closed untuk security, netral untuk sosial) sesuai panduan.
"""
from __future__ import annotations
from ..scorer import TokenFeatures

def build_features(ca: str, chain: str, market: dict, sec: dict,
                   extra: dict | None = None) -> TokenFeatures:
    ex = extra or {}
    buys = int(market.get("buys_5m", 0) or 0)
    sells = int(market.get("sells_5m", 0) or 0)
    uniq = buys + sells
    vol5 = float(market.get("volume_5m", 0) or 0)
    liq = float(market.get("liquidity_usd", 0) or 0)
    # volume spike kasar vs likuiditas (proksi turnover 5m)
    turnover = (vol5 / max(market.get("mcap", 0) or 0, 1.0)) * 100
    spike = 3.5 if turnover > 15 else (2.2 if turnover > 6 else 1.0)
    fomo = bool(market.get("price_change_5m", 0) and float(market["price_change_5m"]) > 100)
    # fee_ratio default organik bila tak ada data wash (DexScreener tak beri globalFees)
    fee_ratio = float(ex.get("fee_ratio", 0.95))
    return TokenFeatures(
        ca=ca, chain=chain, symbol=market.get("symbol", ex.get("symbol", "")),
        mcap=float(market.get("mcap", 0) or 0),
        liquidity_usd=liq,
        lp_locked_pct=float(ex.get("lp_locked_pct", 85.0)),
        lp_burned=bool(ex.get("lp_burned", False)),
        honeypot=bool(sec.get("honeypot", False)),
        mint_unlimited=bool(sec.get("mint_unlimited", False)),
        blacklist=bool(sec.get("blacklist", False)),
        can_freeze=bool(sec.get("can_freeze", False)),
        proxy_risky=bool(sec.get("proxy_risky", False)),
        buy_tax=float(ex.get("buy_tax", 0.0)),
        sell_tax=float(ex.get("sell_tax", 0.0)),
        top1_pct=float(sec.get("top1_pct") or ex.get("top1_pct", 3.5)),
        dev_pct=float(ex.get("dev_pct", 2.0)),
        holders=int(ex.get("holders", 300)),
        top10_virgin_ratio=float(ex.get("top10_virgin_ratio", 0.1)),
        holder_growth_15m=int(ex.get("holder_growth_15m", 60)),
        bundle_max_cluster_pct=float(ex.get("bundle_max_cluster_pct", 8.0)),
        bundle_cluster_count=int(ex.get("bundle_cluster_count", 1)),
        fee_ratio=fee_ratio,
        unique_wallets_5m=int(ex.get("unique_wallets_5m", uniq or 120)),
        signal_count=int(ex.get("signal_count", 3 if uniq > 80 else 0)),
        signal_distinct_wallets=bool(ex.get("signal_distinct_wallets", True)),
        jp_wallet_count=int(ex.get("jp_wallet_count", 1 if uniq > 150 else 0)),
        whale_inflow=bool(ex.get("whale_inflow", liq > 40000)),
        kol_tagged_inflow=bool(ex.get("kol_tagged_inflow", False)),
        mention_per_hour=int(ex.get("mention_per_hour", 20 if uniq > 100 else 2)),
        kol_legit_shill=bool(ex.get("kol_legit_shill", False)),
        kol_dumper_shill=False,
        cabal_edge=bool(ex.get("cabal_edge", False)),
        dex_boost_early=bool(ex.get("dex_boost_early", True)),
        dex_boost_after_pump=bool(ex.get("dex_boost_after_pump", fomo)),
        community_healthy=bool(ex.get("community_healthy", uniq > 100)),
        volume_spike_mult=float(ex.get("volume_spike_mult", spike)),
        fomo_top=bool(ex.get("fomo_top", fomo)),
        dip_state=str(ex.get("dip_state", "dip2_ok" if not fomo else "none")),
        at_support=bool(ex.get("at_support", not fomo)),
        risk_reward=float(ex.get("risk_reward", 3.0)),
        narrative=str(ex.get("narrative", "default")),
        extra={"turnover_5m": round(turnover, 2), "dex": market.get("dex", ""),
               "price": float(market.get("price") or 0)},
    )

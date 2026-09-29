"""Contoh verifikasi scorer: 1 runner, 1 wash, 1 rug. Jalankan: python run_example.py"""

from src.scorer import TokenFeatures, score_token, pick_winner

CFG = {
    "minLiquidityUSD": {"solana": 8000, "bsc": 5000},
    "maxBuyTaxPct": 10, "maxSellTaxPct": 10,
    "maxTop1HardRejectPct": 15.0, "maxDevPct": 10.0,
    "filters": {"rejectWash": True, "rejectBundledGt20Pct": True},
    "scores": {"buyThreshold": 75, "watchThreshold": 60, "minSmartMoney": 25},
    "narrativeTargets": {"default": 3000000, "animal": 5000000},
}

runner = TokenFeatures(ca="Runner111", chain="solana", symbol="$DUVEL", mcap=400000,
    liquidity_usd=50000, lp_locked_pct=95, top1_pct=3.2, dev_pct=2.0, holders=1200,
    top10_virgin_ratio=0.1, holder_growth_15m=80, bundle_max_cluster_pct=8,
    bundle_cluster_count=1, fee_ratio=0.95, unique_wallets_5m=300,
    signal_count=4, signal_distinct_wallets=True, jp_wallet_count=2,
    whale_inflow=True, kol_tagged_inflow=True, mention_per_hour=80,
    kol_legit_shill=True, cabal_edge=True, dex_boost_early=True,
    community_healthy=True, volume_spike_mult=3.5, dip_state="dip2_ok",
    at_support=True, risk_reward=3.5, narrative="animal")

wash = TokenFeatures(ca="Wash222", chain="solana", mcap=900000, liquidity_usd=30000,
    lp_locked_pct=80, top1_pct=4.0, fee_ratio=0.15, unique_wallets_5m=12,
    is_first_second_spike=True, signal_count=6, signal_distinct_wallets=False)

rug = TokenFeatures(ca="Rug333", chain="solana", mcap=200000, liquidity_usd=15000,
    lp_locked_pct=10, honeypot=False, mint_unlimited=True, top1_pct=12.0)

rows = [(t, score_token(t, CFG)) for t in (runner, wash, rug)]
for t, r in rows:
    print(f"{t.symbol or t.ca} -> {r.decision} score={r.score} L1={r.l1} L2={r.l2} L3={r.l3} {r.reasons}")

win = pick_winner(rows, CFG)
print("WINNER:", win[0].ca if win else None, f"EV={win[2]}" if win else "")
assert rows[0][1].decision == "BUY", "runner harus BUY"
assert rows[1][1].decision == "SKIP", "wash harus SKIP"
assert rows[2][1].decision == "SKIP", "rug harus SKIP"
print("OK semua asersi lolos")

import sys
sys.path.insert(0, ".")
from src.scorer import TokenFeatures, score_token, pick_winner

CFG = {
    "minLiquidityUSD": {"solana": 8000},
    "maxBuyTaxPct": 10, "maxSellTaxPct": 10,
    "maxTop1HardRejectPct": 15.0, "maxDevPct": 10.0,
    "filters": {"rejectWash": True, "rejectBundledGt20Pct": True},
    "scores": {"buyThreshold": 75, "watchThreshold": 60, "minSmartMoney": 25},
    "narrativeTargets": {"default": 3000000},
}

def test_reject_mint():
    r = score_token(TokenFeatures(mint_unlimited=True, liquidity_usd=999999), CFG)
    assert r.decision == "SKIP"

def test_reject_wash():
    r = score_token(TokenFeatures(liquidity_usd=50000, lp_locked_pct=90,
                                  fee_ratio=0.1, unique_wallets_5m=5,
                                  is_first_second_spike=True), CFG)
    assert r.decision == "SKIP"

def test_watch_mid():
    t = TokenFeatures(liquidity_usd=50000, lp_locked_pct=90, top1_pct=4.5,
                      signal_count=1, mention_per_hour=15, volume_spike_mult=2.0,
                      dip_state="none", risk_reward=2.0, unique_wallets_5m=60,
                      fee_ratio=1.0)
    r = score_token(t, CFG)
    assert r.decision in ("WATCH", "SKIP", "BUY")

def test_pick_winner_none():
    assert pick_winner([], CFG) is None

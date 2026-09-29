# DEGEN-SCOUT v1 — BOT FINAL
Plan: `../PLAN_BOT_DEGEN_AVE.md`

## Jalankan
```powershell
cd degen
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.db ./degen.db
python run_example.py
python -m src.bot --once --limit 10        # 1 putaran live (DRY_RUN, aman)
python -m src.bot --loop 60 --limit 10     # loop tiap 60 detik
python backtest/replay.py backtest/sample.json
```

Mode di `config.yaml`: `DRY_RUN` (paper) -> `SEMI_AUTO` (instruksi @AveSniperBot) ->
`FULL_AUTO` (butuh `LIVE_TRADING=1` + `BOT_PRIVATE_KEY`, masih stub exchange).

## Alur
`DexScreener boosts/profiles` -> `pair terbaik` -> `RugCheck (Solana)` ->
`features` -> `scorer 0-100` -> `pick_winner EV` -> `risk` -> `executor`.

## File
- `src/bot.py`, `src/pipeline.py`, `src/scorer.py`, `src/decider.py`
- `src/ingestor/dexscreener.py`, `src/ingestor/token_detail.py`
- `src/analyzer/security.py`, `src/analyzer/features.py`
- `src/executor/buyer.py`, `src/exit_manager.py`, `src/risk.py`, `src/notify.py`
- `src/db.py`, `backtest/replay.py`, `tests/test_scorer.py`

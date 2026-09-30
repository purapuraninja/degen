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

## Helius (holder + authority real, Solana)
Key di `.env` (`HELIUS_API_KEY=...`, file ini gitignored). Modul `src/ingestor/helius.py`:
deep-dive hanya untuk kandidat Solana lolos awal (skor >= watch) -> timpa default
dengan `getTokenLargestAccounts` (top1%), DAS `getAsset` (mint/freeze authority +
supply cadangan), aproksimasi holder count, virgin ratio top-10, cluster funder
(bundle, hanya untuk kandidat BUY). Gagal/rate-limit -> fallback heuristik, bot
tetap jalan. Status 2026-09-30: key valid (`getHealth ok`) tapi node Helius
mengembalikan state salah (BONK tak ketemu, supply WSOL 0) — kemungkinan insiden
sementara; pantau https://status.helius.dev/ lalu uji ulang `python -m src.bot --once --limit 3`
dan cari baris `[HELIUS]` di log.

## File
- `src/bot.py`, `src/pipeline.py`, `src/scorer.py`, `src/decider.py`
- `src/ingestor/dexscreener.py`, `src/ingestor/token_detail.py`, `src/ingestor/helius.py`
- `src/analyzer/security.py`, `src/analyzer/features.py`
- `src/executor/buyer.py`, `src/exit_manager.py`, `src/risk.py`, `src/notify.py`
- `src/db.py`, `backtest/replay.py`, `tests/test_scorer.py`, `tests/test_helius.py`

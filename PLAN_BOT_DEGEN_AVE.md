# PLAN BOT DEGEN — Auto Reader, Analyzer & Buyer Memecoin
> Disusun dari analisa menyeluruh **"Kitab Degen: Pedoman Profit dari Memecoin / 0-1Million with Ave"** — Ave Indonesia (Notion: `five-jaw-2d8`, ±33 bab)
> Tujuan bot: **membaca semua koin baru/trending → menganalisa seperti SOP degen pro → memutuskan 1 koin dengan expected profit terbesar → auto-buy dengan manajemen risiko.**

Tanggal: 2026-09-29
Status: PLAN (belum implementasi)

---

## 0. Ringkasan Hasil Analisa Panduan

### 0.1 Struktur Panduan Asli
Panduan terbagi 5 kelompok besar:

1. **Fondasi Mental & On-Chain (Bab 1-4)**
   - `1. Pendahuluan`: Era Trump memecoin Jan 2025, BNB/Solana/Base bersaing, puluhan ribu koin/hari → butuh screening cepat.
   - `2. Pengetahuan Awal On-Chain`: transaksi permanen, tanpa perantara, transparan, tanpa KYC, gap informasi = peluang.
   - `3. MEME = MELATIH MENTAL`: memecoin = tokenisasi hype. Nilai = sentimen komunitas + sosmed + influencer + momentum. Contoh $BONK, $SHIB.
   - `4. Mengirim Token ke Wallet Web3`: alur CEX (Indodax/Binance/Pintu) → beli SOL/BNB → kirim ke wallet Ave.ai per-chain.
   - `Sepatah duapatah words / How to survive`: Jangan ALL IN, TP bertahap, fee DEX ada 3 (gas+slippage+dexfee), trendline jebol = jual, PVP ticker sama = hindari, DCA jual juga penting.

2. **Ekosistem Ave.ai (Bab 5-9, 12)**
   - `5. Ave.ai`: agregator multi-chain 100+ chain, screening+trading+analisis satu tempat. Entry: BOT Wallet / Wallet (QR) / Watch Address. App: Create Bot Wallet / Create New Wallet / Import / Observe.
   - `6. Kenapa harus pakai ave.ai`: Masalah ritel = tools terpisah (chart ≠ audit ≠ eksekusi → entry telat). Solusi: **cek → beli → pantau** dalam 1 alur, fee **0.8%** vs standar 1% (hemat ~20% compounding).
   - Trio Bot:
     - `@AveTokenFinderBot` (Smart Audit): cek honeypot, LP lock, ownership/renounce, backdoor mint, skor AI.
     - `@AveSniperBot` (Fast Trade): eksekusi milidetik, 16 chain, cross-chain otomatis (dana di Solana bisa entry Base tanpa CEX), copy-trade, TP/SL otomatis (Sleep Order).
     - `@AveaiBuyBot` (Radar): alert token baru, alert harga (mis. break ATH), monitoring whale.
   - `7. Tampilan Website`: Identitas Token (nama/CA/logo/sosmed/harga/PnL/SC reader) + Chart (TF, indikator TradingView gratis, tombol fast buy/sell) + Order Book (txns/holders/LP) + Metrik Pasar + Metrik On-chain (SC/fee/holders/LP).
   - `8. Tampilan Aplikasi`: sama + filter holders + Analisis Risiko (Review/Audit).
   - `9. Bot Telegram`: Chain (BSC/Solana/Base/ETH/Ton/Core/Tron/Sui), My Assets, Smart Sniper (beli listing baru super cepat), Buy/Sell, Limit Order, Copy Trade, Auto Sell, Transfer/Receive, Referral, Settings (slippage, anti-MEV, security password), Switch Bot.
   - `12. pro.ave.ai`: hubungkan website + bot untuk sinkron wallet & sinyal.

3. **SOP Screening Inti (Bab 10, 13, 14) — Jantung Bot**
   - `10. Cara Screening (Narasi dan Smartcontract)`:
     1. Cek sosmed dulu: search CA di Twitter, akun asli vs bot? KOL berkualitas atau tukang rug? Ada koneksi antar KOL/Cabal? Cek `pumpscam.com` untuk tweet dihapus.
     2. Greenflag distribusi: 1 wallet tidak >5%, ideal top holders <4%, Top 10 bukan virgin wallet (umur pendek).
     3. Scan bundle via Bubble Maps (gratis di Ave.ai): dot tidak terhubung = sehat, banyak nyambung = 1 entitas.
     4. Cek posisi harga: TA dasar support/resistance, **beli hanya di support zone**, chart TradingView di Ave gratis.
     5. Cek KOL shill-and-dump.
     6. Cek holders: siapa hold? whale? winrate? dana besar?
   - `13. Analysis Tools`: label `Audit/Review` dari tim Ave + **Smart Contract Reader**: Honeypot, Open Source, Cannot Tamper Balance, Not Proxy, Slippage, No Whitelist, No Blacklist, Mint/Minting (batas supply jelas?), Cannot Take Back Ownership (Renounced), No Trading Cooldown.
   - `14. Smart Money Tracker`: pilih token naik/volume signifikan → buka Holders → cek Total PnL → Realized vs Unrealized → kolom Bought (cth: beli 1 SOL → jual 100 SOL = JP 100x). Fitur `Smarters / Signal Center`: jika >1 smart wallet beli token sama → notifikasi. `KOL & Top Traders`: intip apa yang mereka beli & JP dari apa. Cari whale (balance SOL besar), tandai **JP Wallet** untuk di-follow.

4. **Gaya Trading & Psikologi (Bab 11, 16, Trading Memecoin)**
   - `High Volume`: scalping TF 1-5m, pantau Top Gainers/Trending Volume Ave.ai, pastikan likuiditas cukup, TP/SL sebelum entry. Contoh: volume +300%/10 mnt, candle naik beruntun → beli → TP 20-30%. Risiko: volume manipulasi bot/dev/whale, pump & dump.
   - `Trend Spotting`: pantau X/TikTok/Discord/Telegram alpha (`@aveai_indonesia`), tools: Ave.ai, LunarCrush, Google Trends. Contoh Kekius Maximus (Elon). Risiko: hype hilang → dump, scam menyamar tren.
   - `Cult Community`: komunitas fanatik > fundamental. Contoh Sigma (Murad), WIF, PEPE. Identifikasi: aktivitas (meme/shill/event), narasi konsisten, tokoh sentral, volume stabil saat market turun. Risiko: fake aktif (bot), burn out.
   - `CTO (Community Take Over)`: koin mati dihidupkan lagi oleh influencer/whale. Prinsip "never sell your dust". Kadang лучше diamkan daripada cut loss di pucuk.
   - `Buy the Dip → Sell Higher`: akumulasi saat sideways/floor price, pilih koin berumur + komunitas kuat. Sabar tapi konsisten.
   - `Tebar Jala`: pecah modal (cth: 1 SOL → 5 koin @0.2) biarkan run. Cocok modal besar, tidak mau mantengin chart.
   - `16. Degen Trading`: spekulatif ekstrem, entry/exit menit-jam, FOMO tanpa riset = contoh beli $X viral → bisa +5x atau -90% (rug). Aset: memecoin low-cap, meme stocks, leverage.
   - `Meme vs Utility`: pertanyaan salah. Tanya: mana sesuai style & skill? Saran Ponyin: mulai dari meme untuk melatih psikologi & risk management dengan uang sungguhan, baru ke utility.

5. **Deteksi Manipulasi Lanjutan (Sumber Ponyin.id)**
   - `Bundle Token`: 1 orang kontrol puluhan wallet beli di milidetik pertama. Terlihat organik padahal 1 komando. Patokan "holder <3%" usang — 1 orang bisa 5-20 wallet @2% = total 20-40%. Untuk narasi besar, 7-10%/wallet masih wajar. Pemain new-pair (Cupsey, Cented, Log, Decu) beli agresif detik pertama = PvP murni.
   - `Revoke & Minting`: Revoke ≠ aman. Revoke = dev tidak bisa freeze/blokir (checklist RugCheck), tapi **tidak cegah dump supply yang sudah dipegang**. Mint Authority aktif = bisa cetak tanpa batas → dilusi → red flag besar.
   - `Global Fees`: fee Solana ~0.25% ke pool (Raydium/Orca). Analogi struk pajak: volume Rp100jt tapi pajak Rp10rb = bohong. Tipe: Organik (fee sebanding, banyak wallet, chart naik seiring volume), Wash Trading (volume tinggi fee kecil, wallet sama saling jual-beli), Bot Pump (volume meledak detik pertama fee tidak sebanding).
   - `Dex Paid, Ads & Boost`: alat marketing berbayar, bukan bukti kualitas. Bahaya jika muncul **setelah pump besar** = distribusi/exit liquidity. Positif jika muncul **di awal launch** + narasi genuine + komunitas organik = komitmen dev.
   - `3 Konfirmasi Candle`: Dip1 = jangan masuk (hampir selalu ada dip2 lebih bawah). Bounce = masuk 10% saja (mark position). Dip2 (area mirip dip1, tidak jebol jauh) = entry penuh. Jika dip2 jebol jauh = mundur, rugi hanya 10% (cth: 0.1 SOL dari rencana 1 SOL). Mengubah worst-case dari boncos total → boncos terkendali (90% → 50/50).
   - `Cabal Play`: kelompok tertutup rencanakan deploy-timing-exit. Tipe: solo whale (cth: Duvel vs vamp di $YARANAIKA, pump sendirian), dsb. Cara manfaatkan: pelajari range push historis, monitor konflik antar cabal (konflik = bensin volume), **track wallet bukan FOMO token** (ketinggalan runner → buka tab transaksi → cari wallet masuk pertama → track untuk next play).
   - `Cara mendapat koneksi CABAL`: Bermodal (beli 0.5-1% supply jadi top holder → diajak circle, gabung VIP/paid, sponsor KOL), Tanpa modal (jadi shiller sukarela, kerja di project mereka, bangun personal brand, jadi bridge/connector).
   - `Ave Signal Monitor`: sinyal jika token dibeli smart wallets. Logika: frekuensi sinyal + jumlah wallet + mcap + inflow (tandai KOL Tiongkok + wallet lain). Aturan praktis: **sinyal 2-5x dari wallet berbeda = perhatian pasar = potensi runner**. Support pumpfun/bonfun/boopfun/fourmeme, SOL & BSC. Bot: `@AveSignalMonitor`. Catatan: hanya works di bull? Harus backtest sendiri, bukan jaminan 100%.
   - Lainnya: `Dusting Token` (kirim receh untuk track/phishing, jangan interaksi/approve), `Simbol` Ave, `Kamus Gaul` (wajib jadi enum/kamus bot: ATH, FDV, LP, MEV, turnover%, dll), `Mekanisme Konsensus` (PoW/PoS/DPoS/PoA/PoH/PoB — konteks chain), `Airdrop` (holder/activity/invite/snapshot, waspada palsu), `Trading di Website` (social tracker, smart wallet reading).

### 0.2 Prinsip yang Wajib Dipegang Bot
1. **Speed > perfection**: puluhan ribu koin/hari → pipeline harus <30 detik dari deteksi → keputusan.
2. **Filter negatif dulu**: 95% koin adalah scam/rug/wash. Tugas utama bot = **menolak**, bukan memilih.
3. **Jangan blind buy**: tidak ada CA tanpa audit + distribusi + likuiditas check.
4. **Beli hanya dengan konfirmasi**: support + smart money inflow + fee organik + bundle sehat.
5. **Position sizing & exit disiplin**: +100% jual 50% (moonbag), SL 20%, DCA jual bertahap via bot agar tidak merusak chart.
6. **Track orang, bukan sekadar token**: JP wallet, KOL, cabal wallet adalah alpha abadi.

---

## 1. Visi & Scope Bot

**Nama kode: DEGEN-SCOUT v1**

**Fungsi utama (sesuai permintaan):**
1. `READ`: membaca/monitoring semua koin baru + trending lintas chain.
2. `ANALYZE`: menilai tiap koin dengan skor profitabilitas (0-100) berbasis 6 pilar panduan.
3. `DECIDE & BUY`: memilih 1 koin dengan skor tertinggi & lolos semua hard-filter → eksekusi beli otomatis dengan sizing + TP/SL.

**Non-goals v1 (jangan dikerjakan dulu):**
- Leverage / futures.
- Auto-shill / auto-post sosmed.
- Cross-chain bridging sendiri (pakai fitur cross-chain AveSniperBot).

**Chain prioritas v1:** Solana (utama, pumpfun/bonkfun/boopfun) + BSC (fourmeme) → sesuai Signal Monitor. Base/ETH menyusul v2.

---

## 2. Arsitektur Sistem

```
[Sumber Data] → [Ingestor] → [Normalizer + Cache] → [Filter Cepat L0] → [Analisis Mendalam L1-L3] → [Scoring] → [Decision] → [Executor] → [Monitor & Exit]
                     ↑                                                                               ↓
                 [DB: tokens, wallets, signals, trades] ←———— [Risk Manager + Logger + Dashboard/Telegram]
```

**Komponen:**

| Komponen | Tugas | Sumber Panduan |
|---|---|---|
| `ingestor-newpair` | Polling token baru tiap 5-15 detik | Signal Monitor (pumpfun, bonkfun, fourmeme), Trending Volume Ave |
| `ingestor-trend` | Trending, Top Gainers, sosial viral | Gaya Trading 1-3, LunarCrush, X/TikTok |
| `security-filter` | Hard reject scam | Bab 13 + Revoke/Mint + Honeypot |
| `distribution-filter` | Bundle, holder, wash | Bab 10 + Bundle + Global Fees |
| `social-narrative` | KOL, cabal, narasi | Bab 10 + Cabal Play |
| `smartmoney` | JP wallet, inflow, signal count | Bab 14 + Signal Monitor |
| `technical` | 3-candle, support, volume | Bab 10.4 + 3 Konfirmasi |
| `scorer` | Gabung jadi 0-100 | Sintesis semua |
| `decider` | Buy / Skip / Watchlist | SOP 3 Langkah Ave |
| `executor` | Beli via AveSniperBot/API/DEX | Bab 6 SOP |
| `exit-manager` | TP/SL bertahap, trailing, CTO-dust | Moonbag/Take initials, Sepatah words |

---

## 3. Data yang Dibaca Bot (READ)

### 3.1 On-Chain / Market (wajib real-time)
- **Identitas:** nama, simbol, CA, chain, logo, decimals, deployer, pool address, DEX (Raydium/Orca/Pancake/Uniswap).
- **Harga & pasar:** price, mcap, FDV, liquidity (USD + % locked + durasi lock), volume 1m/5m/15m/1h/24h, txns (buy/sell count), turnover% = volume/mcap, price change, ATH distance.
- **Holders:** count, growth/menit, top1%, top10%, virgin wallet ratio (umur <24j), % dev/team.
- **LP:** locked? %, platform lock (PinkLock/Uncx/Team Finance), burn?
- **Fee/Tax:** buyTax, sellTax, buyGas, sellGas, globalFees (Solana), slippage aktual.
- **SC flags:** honeypot, openSource, proxy?, canTamperBalance?, canMint?, mintAuthority?, freezeAuthority/revoke?, blacklist?, whitelist?, cooldown?, ownership renounced?
- **Dex marketing:** dexPaid? ads? boost/trending? timestamp munculnya (awal vs setelah pump).
- **Bubble map:** cluster count, % supply per cluster, Gini.

**Sumber teknis:**
- Utama: Ave.ai (scrape/API tidak resmi + `@AveTokenFinderBot` sebagai oracle), DexScreener API (`/token-boosts`, `/tokens`, `/orders`), Birdeye, Helius (Solana), Moralis/Bitquery (EVM), Solscan/Etherscan/BscScan, RugCheck API.
- Bundle: BubbleMaps API + heuristik sendiri (lihat §5).

### 3.2 Smart Money & Signal
- **Signal count:** berapa kali token muncul di `@AveSignalMonitor` / `Smarters` dalam 1h/24h. Syarat runner: 2-5x wallet berbeda.
- **Inflow:** list wallet masuk + label (KOL CN, cabal, whale, JP wallet).
- **Wallet intel:** balance SOL/BNB, total PnL, realized/unrealized, winrate, avg JP (cth: 1→100 SOL), umur wallet, frekuensi trade, token yang sedang di-hold.
- **KOL & Top Traders:** apa yang mereka beli 24h terakhir, dari token apa mereka JP.

### 3.3 Sosial / Narasi
- **X/Twitter:** search CA, mention count/jam, akun asli vs bot (followers, umur, engagement), KOL quality score (histori shill rug vs legit), koneksi antar KOL (graph), tweet dihapus (`pumpscam.com` pattern).
- **Telegram/Discord:** member growth, pesan/menit, bot ratio, admin activity.
- **TikTok/Google Trends/LunarCrush:** social volume, sentiment, galaxy score.
- **Narasi tag:** animal, politik (Trump/Elon/CZ), nostalgia, cult (Sigma/WIF/PEPE style), CTO revival.

Simpan kamus degen (`Kamus Gaul`) sebagai enum di kode agar log terbaca manusia.

---

## 4. Pipeline Keputusan (ANALYZE → DECIDE)

### 4.1 Level 0 — Hard Reject (<1 detik, murah)
Tolak langsung jika salah satu true (skip, catat alasan):

```
IF honeypot == true → REJECT (tidak bisa jual)
IF cannotBuy == true OR cannotSell == true → REJECT
IF mintAuthority == true AND supplyCap == null → REJECT (bisa cetak tanpa batas)
IF blacklist == true OR canFreeze == true → REJECT
IF proxy == true AND implementationChangeable == true → REJECT (bisa diubah diam-diam)
IF buyTax > 10% OR sellTax > 10% → REJECT (kecuali whitelist cult + manual override)
IF liquidityUSD < MIN_LIQ (mis: $8k SOL, $5k BSC) → REJECT
IF lpLockedPercent < 70% AND lpBurned == false → REJECT
IF top1Holder > 15% (non-LP, non-CEX) → REJECT
IF devHold > 10% → REJECT
IF globalFeesAnomaly == WASH (volume tinggi fee tiny, wallet sama) → REJECT
IF dustingPattern == true → REJECT + blacklist CA
```

Nilai `MIN_LIQ`, tax, holder% bisa di-config per-chain (lihat §7).

### 4.2 Level 1 — Distribusi & Manipulasi (skor 0-30)
**A. Holder health (0-10):**
- top1 <4% = 10, 4-5% = 7, 5-8% = 3, >8% = 0 (sesuai greenflag Bab 10).
- Top10 virgin ratio: 0% virgin = +bonus, >30% virgin = -5.
- Holder growth: +50 holders/15mnt organik = bullish.

**B. Bundle / cluster (0-10):**
- Gunakan BubbleMaps + heuristik sendiri:
  - Cluster jika: funded by same deployer/funder dalam 24h + timing buy <60 detik setelah launch + amount mirip + interaksi antar wallet.
  - Skor: 0 cluster dominan (>20% supply/cluster) = 10, 1 cluster 10-20% = 5, >20% atau >3 cluster terhubung = 0 + flag `BUNDLED`.
- Catatan panduan: jangan kaku 3% — untuk narasi besar 7-10%/wallet masih wajar. Maka threshold adaptif: `maxTop = 4% + 0.5 * narrativeStrength (0-6)`.

**C. Volume authenticity via Global Fees (0-10):**
- Hitung `expectedFee = volume * 0.0025` (Solana). `ratio = actualGlobalFees / expectedFee`.
- ratio 0.7-1.3 + uniqueWallets >100 + buy/sell seimbang = 10 (Organik).
- ratio <0.3 + sedikit wallet berulang = 0 (Wash).
- Spike detik pertama tanpa fee sebanding = 0 (Bot Pump).

### 4.3 Level 2 — Smart Money & Sosial (skor 0-40, bobot terbesar)
Ini pembeda profit menurut panduan (Bab 14 + Signal Monitor + Cabal).

**A. Signal frequency (0-12):**
- count 0 = 0, 1 = 4, 2-5 wallet berbeda = 12, >5 dalam 10mnt tapi wallet sama = 2 (kemungkinan wash/boost bayaran).

**B. Wallet quality (0-14):**
- Tiap inflow wallet diberi `walletScore` dari historis: winrate, total PnL, max JP, balance.
  - JP wallet (pernah 50x+): +5 per wallet, max 10.
  - Whale (balance >100 SOL): +2.
  - KOL CN/cabal terlabel Ave: +2.
  - Virgin/low-history: 0 atau -2.
- Agregat: ambil top-3 inflow terbaru.

**C. Sosial/narasi (0-14):**
- Mention velocity (CA search/jam): >50 organik = 6, 10-50 = 3, <10 = 0.
- KOL quality: KOL legit (histori tidak rug) shill = +4, KOL tukang dump = -5 (gunakan `pumpscam` + DB internal).
- Cabal graph: ada edge antar 2+ KOL/caller + timing bersamaan = +4 (potensi coordinated push).
- DexPaid timing: awal launch + organik = +2, setelah pump +50% = -5 (jebakan distribusi).
- Community health (jika ada TG/Discord): pesan organik/menit, meme production, admin aktif = +2.

### 4.4 Level 3 — Teknikal Entry (skor 0-30)
**A. Trend & momentum (0-10):**
- Volume +200-300%/10mnt + candle naik beruntun TF 1m + turnover% tinggi + likuiditas cukup = momentum long.
- Jangan beli di puncak FOMO: jika +100% dalam 5mnt tanpa pullback → skor 0, masuk watchlist tunggu dip.

**B. 3 Konfirmasi Candle (0-12) — implementasi kode:**
```
state = DIP1_DETECTED? -> tunggu
BOUNCE? -> beli 10% (mark position)
DIP2 in [dip1_low*0.95, dip1_low*1.05] and not breakdown -> full entry signal = 12
DIP2 breakdown jauh (>10% di bawah dip1) -> ABORT, cut 10% tadi
```
- Beli hanya di support zone (pivot/low sebelumnya, round number, floor sideways). Resistance = jangan market buy, pasang limit.

**C. Risk/Reward (0-8):**
- Hitung SL (di bawah dip2 - buffer) vs TP1 (+50%), TP2 (+100%), moonbag runner (+300%+).
- R:R <1:2 → skor 0. R:R >1:3 → 8.

### 4.5 Skor Akhir & Keputusan BUY

```
total = L1 (30) + L2 (40) + L3 (30) = 100
+ bonus CTO-revival (+5 jika komunitas takeover solid + volume stabil)
- penalty PVP (jika >3 ticker sama dalam 24h, -10, volume terpecah)
```

**Aturan beli (default, bisa tuning):**
- `BUY` jika: total >= 75 DAN lolos L0 DAN L2 >= 25 DAN likuiditas cukup DAN bukan wash/bundled.
- `WATCHLIST` jika: 60-74 → pantau 30-120 menit, alert jika signal count bertambah atau dip2 terbentuk.
- `SKIP` jika: <60 atau L0 reject.

**Pilih 1 pemenang:** jika >1 kandidat BUY dalam window (mis: 5 menit), pilih dengan `expectedValue = total * log(mcap upside) / risk`. Upside = (target mcap narasi sejenis / mcap sekarang). Contoh: meme animal rata-rata runner 500k→5M = 10x. Jangan selalu pilih mcap terkecil — likuiditas & LP lock wajib.

---

## 5. Detail Implementasi per Modul (Checklist Teknis)

### 5.1 Ingestor
- [ ] `solana-newpair-poller`: WebSocket Helius + pumpfun/bonkfun API, interval 5s, simpan `firstSeenAt`.
- [ ] `evm-newpair-poller`: Bitquery/Moralis + fourmeme, interval 10s.
- [ ] `trending-poller`: DexScreener boosts + Ave Trending Volume, interval 30s.
- [ ] `signal-listener`: Telegram listener `@AveSignalMonitor`, `@AveaiBuyBot` (Telethon/Bot API), parse CA + mcap + wallet.
- [ ] Rate limit + deduplication by CA+chain. Simpan mentah ke `tokens_raw`.
- [ ] Target: <15 detik dari launch → masuk antrean analisis.

### 5.2 Security Checker
- [ ] Integrasi RugCheck API + `AveTokenFinderBot` (via Telegram bot send CA → parse balasan: honeypot, LP, ownership, skor AI).
- [ ] EVM: baca kontrak via RPC (`eth_call`, cek `mint`, `blacklist`, `pause`, `proxy` EIP-1967 slot).
- [ ] Solana: baca mint authority/freeze authority via `getAccountInfo`, metadata via Metaplex.
- [ ] Cache 24h per CA. Timeout 3s, gagal = SKIP (fail-closed).

### 5.3 Distribution & Wash Detector
- [ ] Holders snapshot tiap 1 menit (Helius/Solana RPC, BscScan API).
- [ ] Virgin check: umur wallet (firstTx), balance history.
- [ ] Bundle heuristik: graph funder → buyer, timing, amount similarity. Visualisasi ala BubbleMaps (simpan edge list).
- [ ] GlobalFees: ambil fee dari tx pool (Raydium/Orca logs) vs volume. Klasifikasi Organik/Wash/BotPump.
- [ ] DexPaid/Boost timestamp: DexScreener `token-boosts` + catat `boostAt` vs `pumpAt`.

### 5.4 Social & Cabal
- [ ] X search worker: `snscrape` / X API / Nitter fallback, query CA + ticker + `$TICKER`.
- [ ] Bot vs human classifier sederhana: followers, age, tweet/day, engagement ratio.
- [ ] KOL DB: manual + auto (track histori call → rug or runner). Skor -10..+10.
- [ ] Pumpscam worker: cek apakah author pernah hapus tweet shill (jika API tersedia, else heuristik).
- [ ] Cabal graph: Neo4j/SQLite graph KOL↔token↔wallet, deteksi co-buy <5 menit.

### 5.5 Smart Money
- [ ] JP wallet DB: auto-tag jika wallet pernah `bought 1 → sold 100` (scan historis).
- [ ] Realized vs Unrealized: dari holder PnL (Ave holders tab / Birdeye wallet portfolio).
- [ ] Signal aggregator: hitung `signalCountDistinctWallets` per token per jam.
- [ ] Copy-trade ready: jika decider BUY karena 1 whale spesifik, simpan `followWallet` untuk auto-copy next trade.

### 5.6 Technical
- [ ] Candles: Birdeye/DexScreener OHLC 1m/5m, indikator: EMA9/21, RSI, volume MA, support/resistance (pivot + round number).
- [ ] Implementasi `ThreeCandleDip` state machine (lihat §4.4).
- [ ] Filter FOMO: tolak market buy jika `price > ATH*0.9` dan `RSI1m >80` dan belum ada dip.

### 5.7 Executor (BUY)
- [ ] **Opsi A (cepat, disarankan v1):** kirim order ke `@AveSniperBot` via Telegram automation (gramjs/Telethon): set chain → paste CA → set amount + slippage (auto untuk meme/microcap, anti-MEV untuk dana besar) → confirm. Fee 0.8% sudah termasuk.
- [ ] **Opsi B (programmatic):** Jupiter Aggregator (Solana) / Pancake Router (BSC) via private key bot wallet. Perlu handling slippage, priority fee, MEV (Jito bundles / private RPC).
- [ ] Sizing default (sesuai Tebar Jala + 3 Candle):
  - Modal per hari dibagi max 5 play concurrent.
  - Per play: 10% mark di bounce, 90% di dip2 konfirmasi. Atau jika momentum kuat + skor >85: 50/50.
  - Contoh: bankroll 5 SOL → max 1 SOL/play → 0.1 mark + 0.9 full.
- [ ] Setelah beli: otomatis set `Sleep Order`: TP1 +50% jual 25%, TP2 +100% jual 25% (balik modal, sisakan moonbag), SL -20% (auto cut), trailing setelah +200%.

### 5.8 Exit & Monitor
- [ ] `@AveaiBuyBot` watchlist + internal monitor tiap 10s: price, volume drop, whale exit (unrealized→realized besar), LP unlock, mint baru.
- [ ] Aturan缆: trendline jebol → jual (Sepatah words). Jangan hold semua sampai bill mcap — realistis: banyak mentok ratusan K mcap.
- [ ] CTO-dust rule: jika -80% tapi komunitas masih aktif + volume stabil → jangan jual sisa dust (never sell dust), pindah ke `dustBag`.
- [ ] DCA jual bertahap via AveBot agar tidak merusak chart jika pegang supply besar.

---

## 6. Tech Stack Rekomendasi

**Bahasa:** Python 3.11+ (analisis + scoring) + Node/TS opsional untuk listener Telegram cepat.
**Libs:**
- `python-telegram-bot`, `telethon` (listener Signal/Sniper bot)
- `solana-py`, `web3.py`, `aiohttp`, `websockets`
- `pandas`, `pandas-ta`, `networkx` (cabal/bundle graph)
- `sqlite` → `postgres` (produksi), `redis` (cache + queue)
- `loguru`, `prometheus` (metrik)

**Infra:**
- VPS 4vCPU/8GB, RPC premium (Helius/BSC) agar tidak rate-limit.
- Docker Compose: `ingestor`, `analyzer`, `decider`, `executor`, `dashboard`, `db`, `redis`.
- Dashboard: Telegram notifikasi + web mini (Streamlit/FastAPI) untuk approve manual di awal (mode `DRY_RUN` → `SEMI_AUTO` → `FULL_AUTO`).

**Keamanan:**
- Wallet bot terpisah, limit saldo (max 20% bankroll di hot wallet), private key di Vault/env, security password Ave, whitelist withdraw address, kill-switch Telegram `/STOP`.

---

## 7. Konfigurasi Awal (bisa tuning via backtest)

```yaml
chains: [solana, bsc]  # base menyusul
pollIntervalSec: { newPair: 7, trending: 30, signal: 5 }
minLiquidityUSD: { solana: 8000, bsc: 5000 }
minHolders: 80
maxBuyTaxPct: 10
maxSellTaxPct: 10
maxTop1Pct: 5.0
idealTop1Pct: 4.0
maxDevPct: 10.0
minUniqueWallets5m: 50
volumeSpike: { windowMin: 10, mult: 3.0 }
signalRunner: { minCount: 2, maxCount: 5, distinctWallets: true }
scores: { buyThreshold: 75, watchThreshold: 60, minSmartMoney: 25 }
sizing: { maxConcurrent: 5, perPlaySol: 1.0, markPct: 10 }
exit: { tp1Pct: 50, tp1SellPct: 25, tp2Pct: 100, tp2SellPct: 25, slPct: 20 }
filters: { rejectWash: true, rejectBundledGt20Pct: true, rejectDexBoostAfterPump: true }
```

---

## 8. Struktur Repo yang Disarankan

```
degen-scout/
├── README.md
├── config.yaml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingestor/
│   │   ├── solana_newpair.py
│   │   ├── evm_newpair.py
│   │   ├── trending.py
│   │   └── signal_listener.py
│   ├── analyzer/
│   │   ├── security.py
│   │   ├── distribution.py   # holders, bundle, globalFees
│   │   ├── social.py         # X, KOL, cabal, pumpscam
│   │   ├── smartmoney.py     # PnL, JP wallet, inflow
│   │   └── technical.py      # 3-candle, support, momentum
│   ├── scorer.py             # gabung 0-100 + expectedValue
│   ├── decider.py            # BUY/WATCH/SKIP + pilih 1 pemenang
│   ├── executor/
│   │   ├── ave_sniper.py     # via Telegram bot
│   │   ├── jupiter.py        # direct DEX (opsional)
│   │   └── pancake.py
│   ├── exit_manager.py
│   ├── risk.py               # kill-switch, daily loss, dust
│   ├── db.py
│   └── notify.py             # Telegram laporan
├── backtest/
│   ├── dataset_builder.py
│   └── replay.py
├── tests/
└── dashboard/
```

---

## 9. Contoh Pseudocode Scoring (inti permintaan)

```python
def score_token(t) -> dict:
    # L0 hard reject, return {decision: SKIP, reason}
    if t.honeypot or t.mint_unlimited or t.blacklist or t.proxy_risky:
        return skip("security")
    if t.liquidity_usd < MIN_LIQ or t.lp_locked_pct < 70:
        return skip("liquidity")
    if detect_wash(t):  # globalFees ratio + wallet reuse
        return skip("wash")
    if bundle_pct(t) > 20:
        return skip("bundled")

    s1 = holder_score(t) + bundle_score(t) + fee_authenticity(t)  # max 30
    s2 = signal_freq(t) + wallet_quality(t) + social_narrative(t)  # max 40
    s3 = momentum(t) + three_candle(t) + risk_reward(t)  # max 30
    total = s1+s2+s3 + cto_bonus(t) - pvp_penalty(t)

    if total >= 75 and s2 >= 25:
        return {"decision":"BUY","score":total,"reason":explain(t)}
    if total >= 60:
        return {"decision":"WATCH","score":total}
    return {"decision":"SKIP","score":total}

def pick_winner(cands):
    # pilih 1 dengan expected profit terbesar
    scored = [c for c in cands if c.decision=="BUY"]
    if not scored: return None
    for c in scored:
        upside = narrative_target_mcap(c.narrative)/c.mcap
        c.ev = c.score * log(upside+1) / c.risk_factor
    return max(scored, key=lambda x: x.ev)
```

**Contoh log keputusan (wajib disimpan):**
```
[BUY] $DUVEL/SOL 7xK... | score 82 (L1 24/L2 33/L3 25)
 + signal 4x wallet berbeda, JP wallet 2 (120x, 80x), holder top1 3.2%, bundle 8% sehat,
   fee ratio 0.95 organik, KOL legit 2 + cabal edge, dip2 konfirmasi support, R:R 1:3.5
 sizing 1.0 SOL (0.1 mark +0.9 full), TP +50/+100, SL -20%
```

---

## 10. Roadmap Bertahap (aman, tidak langsung full-auto)

**Fase 0 — Persiapan (1-2 hari)**
- Buat wallet bot khusus, isi kecil (0.2-0.5 SOL + sedikit BNB), aktifkan security password Ave, catat seed offline.
- Join `@AveTokenFinderBot`, `@AveSniperBot`, `@AveaiBuyBot`, `@AveSignalMonitor`, grup `@aveai_indonesia`.
- Kumpulkan 50-100 CA historis runner & rug untuk dataset + label KOL/JP wallet awal.

**Fase 1 — MVP Reader (3-5 hari)**
- Ingestor newpair + trending + signal listener jalan, simpan DB, tampilkan di Telegram: `CA | mcap | liq | holders | signalCount`.
- Belum ada auto-buy. Target: latensi <20s, 0 crash 24h.

**Fase 2 — Analyzer + Scoring (1-2 minggu)**
- Implementasi L0 + L1 + L2. Output skor + alasan SKIP/BUY di dashboard. Mode `DRY_RUN` (paper trade).
- Backtest 1 bulan data historis: ukur winrate, avg return, max drawdown, % wash terfilter.

**Fase 3 — Semi-Auto Buy (1 minggu)**
- Bot kirim rekomendasi `BUY` + tombol Approve di Telegram → eksekusi via AveSniperBot. Sizing kecil (0.05-0.1 SOL/play). Uji TP/SL otomatis.

**Fase 4 — Full-Auto + Exit Manager (2 minggu)**
- Aktifkan `FULL_AUTO` dengan batas: max 5 concurrent, max daily loss 15% bankroll, kill-switch.
- Tambahkan L3 teknikal penuh (3-candle live), copy-trade JP wallet, cabal graph.

**Fase 5 — Optimasi**
- Tuning threshold per-chain, tambah Base/ETH, tambah TikTok/LunarCrush sentiment, auto-tag dusting, laporan mingguan PnL + referral fee tracking (farming referral sebagai income tambahan, bukan utama).

---

## 11. Risiko & Kepatuhan (jujur, sesuai panduan)

- **Tidak ada jaminan 100% profit.** Panduan sendiri menegaskan signal hanya alat bantu, hype bisa hilang tiba-tiba, rug pull selalu ada. Target realistis: survive + compounding, bukan tiap trade JP.
- **Risiko teknis:** RPC delay, Telegram automation diblokir, slippage ekstrem, MEV sandwich. Mitigasi: anti-MEV, priority fee dinamis, limit slippage, timeout + fail-closed.
- **Risiko dana:** jangan ALL IN, pisahkan hot wallet, mulai kecil. Dusting: jangan pernah approve/swap token asing tiba-tiba.
- **Legal:** trading memecoin high-risk, pastikan patuh regulasi lokal (pajak, CEX on-ramp). Bot ini tools, bukan financial advice.

---

## 12. Checklist SOP Harian Bot (ringkas untuk ditempel di dashboard)

1. Search CA di X → asli/bot? KOL bagus?
2. Top1 <5%? Top10 virgin? (tolak jika tidak)
3. BubbleMaps → dot nyambung? (tolak jika 1 cluster >20%)
4. GlobalFees → organik? (tolak jika wash/bot pump)
5. Signal 2-5x wallet beda? Ada JP/whale?
6. DexPaid kapan? (awal = ok, setelah pump = tolak)
7. Posisi di support? Sudah 3-candle? (jangan FOMO pucuk)
8. Skor >=75 & L2 >=25? → BUY 1 pemenang, sizing disiplin, TP/SL otomatis.

---

## 13. Langkah Selanjutnya (action untukmu)

- [ ] Tentukan bankroll awal & chain pertama (saran: Solana 2-5 SOL untuk uji).
- [ ] Pilih mode awal: `DRY_RUN` ( disarankan 2 minggu).
- [ ] Minta saya generate: `config.yaml` + skeleton kode `scorer.py` + skema DB, atau langsung scaffold repo `degen-scout/`.
- [ ] Kumpulkan 20 CA contoh (10 runner, 10 rug) untuk kalibrasi threshold.

---

### Sumber Analisis
Semua aturan di atas diturunkan langsung dari bab: Pendahuluan, On-Chain, MEME, Ave.ai, Kenapa Ave, Tampilan Web/App/Bot, Screening, Gaya Trading, Analysis Tools, Smart Money, Dusting, Degen Trading, Referral, Kamus, Sepatah Words, Airdrop, Konsensus, Trading Web/Memecoin, Simbol, CABAL, Signal Monitor, Bundle, Revoke/Mint, Global Fees, Meme vs Utility, DexPaid, 3 Candle, Cabal Play.

> File ini adalah PLAN. Eksekusi butuh RPC premium + pengujian bertahap. Kalau kamu setuju dengan arsitektur ini, langkah implementasi berikutnya adalah scaffold kode MVP.

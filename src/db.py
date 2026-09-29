"""Skema DB SQLite DEGEN-SCOUT v1. Buat via: python -m src.db"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tokens (
  ca TEXT NOT NULL,
  chain TEXT NOT NULL,
  symbol TEXT DEFAULT '',
  name TEXT DEFAULT '',
  first_seen_at TEXT DEFAULT '',
  mcap REAL DEFAULT 0,
  liquidity_usd REAL DEFAULT 0,
  holders INTEGER DEFAULT 0,
  score REAL DEFAULT 0,
  decision TEXT DEFAULT '',
  reason TEXT DEFAULT '',
  PRIMARY KEY (ca, chain)
);
CREATE TABLE IF NOT EXISTS token_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ca TEXT NOT NULL,
  chain TEXT NOT NULL,
  ts TEXT NOT NULL,
  price REAL DEFAULT 0,
  mcap REAL DEFAULT 0,
  volume_5m REAL DEFAULT 0,
  txns_5m INTEGER DEFAULT 0,
  holders INTEGER DEFAULT 0,
  top1_pct REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS wallets (
  address TEXT PRIMARY KEY,
  chain TEXT DEFAULT 'solana',
  label TEXT DEFAULT '',           -- whale | jp | kol_cn | cabal | virgin
  balance_sol REAL DEFAULT 0,
  total_pnl REAL DEFAULT 0,
  winrate REAL DEFAULT 0,
  max_jp_mult REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ca TEXT NOT NULL,
  chain TEXT NOT NULL,
  wallet TEXT DEFAULT '',
  ts TEXT NOT NULL,
  source TEXT DEFAULT ''           -- AveSignalMonitor | Smarters | KOL
);
CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ca TEXT NOT NULL,
  chain TEXT NOT NULL,
  side TEXT NOT NULL,              -- BUY | SELL
  amount_sol REAL DEFAULT 0,
  price REAL DEFAULT 0,
  ts TEXT NOT NULL,
  note TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_signals_ca ON signals(ca, chain);
CREATE INDEX IF NOT EXISTS idx_snap_ca ON token_snapshots(ca, chain, ts);
"""


def init_db(path: str | Path = "./degen.db") -> Path:
    p = Path(path)
    con = sqlite3.connect(p)
    try:
        con.executescript(SCHEMA)
        con.commit()
    finally:
        con.close()
    return p


if __name__ == "__main__":
    import sys
    out = init_db(sys.argv[1] if len(sys.argv) > 1 else "./degen.db")
    print(f"OK init {out}")

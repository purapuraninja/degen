import sys
sys.path.insert(0, ".")
from src.analyzer.goplus import to_flags
from src.analyzer.honeypotis import to_flags as hp_flags
from src.ingestor.token_detail import pair_age_min


def _raw(**kw):
    base = {"is_honeypot": "0", "cannot_sell_all": "0", "cannot_buy": "0",
            "is_mintable": "0", "is_blacklisted": "0", "transfer_pausable": "0",
            "is_proxy": "0", "buy_tax": "0", "sell_tax": "0", "holder_count": 0}
    base.update(kw)
    return {"result": {"0xabc": base}}


def test_goplus_bersih():
    f = to_flags(_raw(holder_count=500), "0xabc")
    assert f["honeypot"] is False
    assert f["mint_unlimited"] is False
    assert f["holders"] == 500


def test_goplus_honeypot():
    assert to_flags(_raw(**{"is_honeypot": "1"}), "0xabc")["honeypot"] is True


def test_goplus_tax_desimal():
    f = to_flags(_raw(**{"buy_tax": "0.05", "sell_tax": "3"}), "0xabc")
    assert abs(f["buy_tax"] - 5.0) < 1e-9, f
    assert abs(f["sell_tax"] - 3.0) < 1e-9, f


def test_goplus_kosong():
    assert to_flags(None, "0xabc") == {}
    assert to_flags({"result": {}}, "0xabc") == {}


def test_pair_age():
    now = 1_000_000_000_000.0
    assert pair_age_min(now - 10 * 60000, now) == 10.0
    assert pair_age_min(None, now) is None
    assert pair_age_min(0, now) is None


def test_honeypotis_bersih():
    raw = {"honeypotResult": {"isHoneypot": False},
           "simulationResult": {"buyTax": 0, "sellTax": 0},
           "summary": {"risk": "low"}}
    f = hp_flags(raw)
    assert f["honeypot"] is False


def test_honeypotis_flag():
    raw = {"honeypotResult": {"isHoneypot": True},
           "simulationResult": {"buyTax": "0.1", "sellTax": 50},
           "summary": {"risk": "high"}}
    f = hp_flags(raw)
    assert f["honeypot"] is True
    assert abs(f["buy_tax"] - 10.0) < 1e-9
    assert hp_flags(None) == {}


def test_blacklist_roundtrip():
    import sqlite3
    import tempfile
    import gc
    import os
    import time
    from src.exit_monitor import (ensure_state, blacklist_after_sl,
                                  is_blacklisted)
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        ensure_state(path)
        assert is_blacklisted(path, "bsc", "C9") is False
        blacklist_after_sl(path, "bsc", "C9", hours=24)
        assert is_blacklisted(path, "bsc", "C9") is True
        assert is_blacklisted(path, "bsc", "C8") is False
    finally:
        gc.collect()
        for _ in range(5):
            try:
                os.unlink(path)
                break
            except OSError:
                time.sleep(0.2)

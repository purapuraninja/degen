import sys
sys.path.insert(0, ".")
from src.ingestor.helius import Helius

def test_pct():
    assert Helius.pct_of("5000", 100000.0) == 5.0
    assert Helius.pct_of("0", 1000.0) == 0.0
    assert Helius.pct_of(None, 0) == 0.0

def test_virgin():
    assert Helius.classify_virgin(2, 3600) is True      # 2 tx, umur 1 jam
    assert Helius.classify_virgin(50, 30 * 86400) is False
    assert Helius.classify_virgin(150, 3600) is False   # histori penuh
    assert Helius.classify_virgin(None, 100) is None
    assert Helius.classify_virgin(5, None) is None

"""Helius deep-dive (Solana): holder real, authority real (DAS), virgin & bundle check.

Sumber panduan: greenflag distribusi top1<5% (Bab 10), virgin wallet, BubbleMaps
bundle, mint/freeze authority (Bab 13 + Revoke/Mint). Menggantikan default
heuristik di features.py dengan observasi on-chain bila HELIUS_API_KEY ada.

Key dibaca dari env / .env, TIDAK pernah di-print atau masuk log.
"""
from __future__ import annotations
import json
import os
import time
import urllib.request
from pathlib import Path

RPC_URL = "https://mainnet.helius-rpc.com/"
REST_URL = "https://api.helius.xyz/v0"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
VIRGIN_MAX_AGE_SEC = 24 * 3600


def load_key() -> str:
    k = os.getenv("HELIUS_API_KEY", "").strip()
    if k:
        return k
    for p in (Path(".env"), Path(__file__).resolve().parents[1] / ".env"):
        try:
            if not p.exists():
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if s.startswith("HELIUS_API_KEY="):
                    v = s.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
        except Exception:
            continue
    return ""


def _redact(msg: str, key: str) -> str:
    try:
        return msg.replace(key, "***") if key else msg
    except Exception:
        return "error"


class Helius:
    def __init__(self, key: str, timeout: int = 15):
        self._key = key
        self.timeout = timeout

    # ---------------------------------------------------------- low level
    def rpc(self, method: str, params: list):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                           "params": params}).encode()
        req = urllib.request.Request(
            RPC_URL + "?api-key=" + self._key, data=body,
            headers={"Content-Type": "application/json",
                     "User-Agent": "degen-scout/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                d = json.loads(r.read().decode("utf-8", "ignore"))
        except Exception as e:
            raise RuntimeError(_redact(f"rpc {method} gagal: {e}", self._key)[:200])
        if isinstance(d, dict) and d.get("error"):
            raise RuntimeError(_redact(f"rpc {method}: {d['error']}", self._key)[:200])
        return d.get("result")

    def rest(self, path: str, qs: str = ""):
        url = f"{REST_URL}{path}?api-key={self._key}" + ("&" + qs if qs else "")
        req = urllib.request.Request(url, headers={"User-Agent": "degen-scout/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except Exception as e:
            raise RuntimeError(_redact(f"rest {path} gagal: {e}", self._key)[:200])

    # ---------------------------------------------------------- pure parse
    @staticmethod
    def pct_of(ui_amount, supply_ui: float) -> float:
        try:
            return float(ui_amount or 0) / max(float(supply_ui or 0), 1e-12) * 100.0
        except Exception:
            return 0.0

    @staticmethod
    def classify_virgin(tx_count: int | None, age_sec: float | None) -> bool | None:
        """True=virgin, False=bukan, None=tak diketahui. Virgin = umur<24j."""
        if tx_count is None or age_sec is None:
            return None
        if tx_count >= 100:
            return False  # histori penuh 100+, wallet aktif
        return age_sec < VIRGIN_MAX_AGE_SEC

    # ---------------------------------------------------------- live calls
    def largest_accounts(self, mint: str, n: int = 20) -> list[dict]:
        res = self.rpc("getTokenLargestAccounts", [mint])
        return (res or {}).get("value", [])[:n]

    def supply_ui(self, mint: str) -> float:
        res = self.rpc("getTokenSupply", [mint])
        return float((res or {}).get("value", {}).get("uiAmountString") or 0)

    def asset_authorities(self, mint: str) -> dict | None:
        """DAS getAsset -> mint/freeze authority + supply. None bila tak terindeks."""
        try:
            res = self.rpc("getAsset", [mint])
        except Exception:
            return None
        if not isinstance(res, dict):
            return None
        ti = res.get("token_info") or {}
        try:
            supply = float(ti.get("supply") or 0) / (10 ** int(ti.get("decimals") or 0))
        except Exception:
            supply = 0.0
        return {"mint_authority": ti.get("mint_authority"),
                "freeze_authority": ti.get("freeze_authority"),
                "supply_ui": supply}

    def holder_count_approx(self, mint: str) -> int | None:
        """Hitung unique owner via getProgramAccounts + dataSlice (aproksimasi)."""
        try:
            res = self.rpc("getProgramAccounts", [TOKEN_PROGRAM, {
                "encoding": "base64",
                "dataSlice": {"offset": 32, "length": 32},
                "filters": [{"memcmp": {"offset": 0, "bytes": mint}},
                            {"dataSize": 165}]}])
        except Exception:
            return None
        owners = set()
        for it in res or []:
            try:
                import base64
                raw = (it.get("account") or {}).get("data", ["", ""])[0]
                owners.add(base64.b64decode(raw).hex())
            except Exception:
                continue
        return len(owners) or None

    def wallet_stats(self, address: str) -> tuple[int | None, float | None]:
        """Return (tx_count, age_sec). Penuh bila histori <100 (punya semua)."""
        try:
            sigs = self.rpc("getSignaturesForAddress", [address, {"limit": 100}]) or []
        except Exception:
            return None, None
        if not sigs:
            return 0, None
        now = time.time()
        oldest = sigs[-1].get("blockTime")
        age = (now - oldest) if oldest else None
        return len(sigs), age

    def first_funder(self, wallet: str) -> str | None:
        """Funder = pengirim native transfer pertama yang masuk (heuristik 1 komando)."""
        try:
            txs = self.rest(f"/addresses/{wallet}/transactions", "limit=25") or []
        except Exception:
            return None
        if not isinstance(txs, list) or not txs:
            return None
        for tx in reversed(txs):  # dari paling lama
            try:
                for nt in tx.get("nativeTransfers") or []:
                    if nt.get("toUserAccount") == wallet and nt.get("fromUserAccount"):
                        return nt["fromUserAccount"]
            except Exception:
                continue
        return None


def deep_dive(mint: str, key: str, top_n: int = 10, with_bundle: bool = False) -> dict:
    """Observasi on-chain untuk 1 token. Semua gagal -> {} (caller pakai default)."""
    h = Helius(key)
    out: dict = {}
    try:
        try:
            supply = h.supply_ui(mint)
        except Exception:
            supply = 0.0
        auth = h.asset_authorities(mint)  # DAS: authority real + supply cadangan
        if supply <= 0 and auth and auth.get("supply_ui"):
            supply = auth["supply_ui"]
        if supply <= 0:
            return {}
        accts = h.largest_accounts(mint, top_n)
        if not accts:
            return {}
        pcts = [Helius.pct_of(a.get("uiAmountString"), supply) for a in accts]
        addrs = [a.get("address", "") for a in accts]
        out["top1_pct"] = round(pcts[0], 3)
        out["top10_pct"] = round(sum(pcts[:10]), 2)
        # virgin ratio top holders
        virgin = 0
        known = 0
        for a in addrs:
            if not a:
                continue
            n, age = h.wallet_stats(a)
            v = Helius.classify_virgin(n, age)
            if v is None:
                continue
            known += 1
            virgin += 1 if v else 0
        if known:
            out["top10_virgin_ratio"] = round(virgin / known, 3)
        # authority real (DAS menimpa heuristik RugCheck bila sukses)
        if auth is not None:
            out["mint_unlimited"] = auth["mint_authority"] is not None
            out["can_freeze"] = auth["freeze_authority"] is not None
        # holder count aproksimasi
        hc = h.holder_count_approx(mint)
        if hc:
            out["holders"] = hc
        # bundle: cluster per funder pertama
        if with_bundle:
            funders: dict[str, float] = {}
            nofund = 0
            for a, p in zip(addrs, pcts):
                if not a:
                    continue
                f = h.first_funder(a)
                if not f:
                    nofund += 1
                    continue
                funders[f] = funders.get(f, 0.0) + p
            if funders:
                out["bundle_max_cluster_pct"] = round(max(funders.values()), 2)
                out["bundle_cluster_count"] = len(funders)
            out["bundle_wallets_unresolved"] = nofund
    except Exception:
        pass
    return out

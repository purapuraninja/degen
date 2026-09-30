"""Dashboard server (stdlib only): serve index.html + JSON API dari degen.db.

Run:
  python dashboard/server.py --port 8080 --db ./degen.db
Buka: http://localhost:8080/
"""
from __future__ import annotations
import argparse
import json
import re
import sqlite3
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from src.config import load_config
from src.exit_manager import check_exit
from src.ingestor.token_detail import fetch_token_pairs, best_pair, pair_to_market

INDEX = HERE / "index.html"
CFG = load_config(str(ROOT / "config.yaml"))


def db_con(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def safe_sym(s: str) -> str:
    return str(s or "?").encode("ascii", "ignore").decode() or "?"


def live_market(chain: str, ca: str) -> dict | None:
    try:
        bp = best_pair(fetch_token_pairs(chain, ca))
        return pair_to_market(bp) if bp else None
    except Exception:
        return None


def buy_qty(note: str | None, amount, price) -> float:
    m = re.search(r"qty=([\d.eE+-]+)", note or "")
    if m:
        try:
            return float(m.group(1))
        except Exception:
            pass
    try:
        return float(amount or 0) / float(price or 0) if price else 0.0
    except Exception:
        return 0.0


def symbol_of(db_path: str, chain: str, ca: str) -> str:
    try:
        con = db_con(db_path)
        r = con.execute("select symbol from tokens where ca=? and chain=?",
                        (ca, chain)).fetchone()
        con.close()
        if r and r["symbol"]:
            return safe_sym(r["symbol"])
    except Exception:
        pass
    return safe_sym(ca[:6])


def build_positions(db_path: str) -> dict:
    """FIFO lots dari tabel trades. SELL menutup lot, sisa = posisi open."""
    try:
        con = db_con(db_path)
        rows = con.execute(
            "select ca,chain,side,amount_sol,price,ts,note from trades order by rowid"
        ).fetchall()
        con.close()
    except Exception:
        rows = []
    lots: dict[tuple, list] = {}
    realized = 0.0
    for r in rows:
        key = (r["chain"], r["ca"])
        lots.setdefault(key, [])
        if (r["side"] or "").upper() == "BUY":
            q = buy_qty(r["note"], r["amount_sol"], r["price"])
            if q > 0:
                lots[key].append([q, float(r["price"] or 0)])
        else:
            m = re.search(r"qty=([\d.eE+-]+)", r["note"] or "")
            q = float(m.group(1)) if m else sum(x[0] for x in lots[key])
            sp = float(r["price"] or 0)
            left = q
            while left > 1e-12 and lots[key]:
                take = min(lots[key][0][0], left)
                realized += (sp - lots[key][0][1]) * take
                lots[key][0][0] -= take
                left -= take
                if lots[key][0][0] <= 1e-12:
                    lots[key].pop(0)
    positions = []
    unreal = 0.0
    for (chain, ca), ls in lots.items():
        oq = sum(x[0] for x in ls)
        if oq <= 0:
            continue
        avg = sum(x[0] * x[1] for x in ls) / oq
        m = live_market(chain, ca)
        cur = (m["price"] if m else None) or None
        nilai = oq * cur if cur else None
        pnl = (nilai - oq * avg) if cur else None
        pnl_pct = ((cur - avg) / avg * 100) if (cur and avg) else None
        status = check_exit(cur, avg, CFG) if cur else "UNKNOWN"
        if pnl is not None:
            unreal += pnl
        positions.append({
            "ca": ca, "chain": chain, "symbol": symbol_of(db_path, chain, ca),
            "mcap": m["mcap"] if m else None,
            "liq": m["liquidity_usd"] if m else None,
            "avg_entry": avg, "qty": oq, "cost": oq * avg,
            "price": cur, "nilai": nilai, "pnl": pnl, "pnl_pct": pnl_pct,
            "exit": status,
        })
    positions.sort(key=lambda p: (p["pnl"] is None, -(p["pnl"] or 0)))
    return {"positions": positions,
            "totals": {"unrealized": unreal, "realized": realized,
                       "total": unreal + realized,
                       "open_count": len(positions)}}


class Handler(BaseHTTPRequestHandler):
    db_path = "./degen.db"

    def _send(self, code: int, body: bytes, ctype: str = "application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            html = INDEX.read_bytes() if INDEX.exists() else b"<h1>index.html missing</h1>"
            return self._send(200, html, "text/html; charset=utf-8")
        if u.path == "/api/stats":
            con = db_con(self.db_path)
            try:
                n = con.execute("select count(*) c from tokens").fetchone()["c"]
                nb = con.execute("select count(*) c from tokens where decision='BUY'").fetchone()["c"]
                nw = con.execute("select count(*) c from tokens where decision='WATCH'").fetchone()["c"]
                nt = con.execute("select count(*) c from trades").fetchone()["c"]
            except Exception:
                n = nb = nw = nt = 0
            finally:
                con.close()
            return self._send(200, json.dumps(
                {"total": n, "buy": nb, "watch": nw, "trades": nt}).encode())
        if u.path == "/api/tokens":
            chain = (q.get("chain", [""])[0] or "").lower()
            search = (q.get("q", [""])[0] or "").lower()
            con = db_con(self.db_path)
            try:
                rows = con.execute(
                    "select ca,chain,symbol,mcap,liquidity_usd,holders,score,decision,reason"
                    " from tokens order by score desc limit 100").fetchall()
            except Exception:
                rows = []
            finally:
                con.close()
            out = []
            for r in rows:
                d = dict(r)
                if chain and d.get("chain") != chain:
                    continue
                if search and search not in ((d.get("symbol") or "") + d.get("ca", "")).lower():
                    continue
                d["symbol"] = safe_sym(d.get("symbol") or d.get("ca", "")[:6])
                out.append(d)
            return self._send(200, json.dumps(out).encode())
        if u.path == "/api/trades":
            con = db_con(self.db_path)
            try:
                rows = con.execute(
                    "select ca,chain,side,amount_sol,price,ts,note from trades"
                    " order by rowid desc limit 30").fetchall()
                out = [dict(r) for r in rows]
            except Exception:
                out = []
            finally:
                con.close()
            return self._send(200, json.dumps(out).encode())
        if u.path == "/api/positions":
            return self._send(200, json.dumps(build_positions(self.db_path)).encode())
        if u.path == "/api/chart":
            import math
            import random
            ca = q.get("ca", [""])[0]
            con = db_con(self.db_path)
            try:
                r = con.execute("select mcap,symbol from tokens where ca=?",
                                (ca,)).fetchone()
                base = float(r["mcap"]) if r and r["mcap"] else 100000.0
            except Exception:
                base = 100000.0
            finally:
                con.close()
            rnd = random.Random(abs(hash(ca)) % (2 ** 32))
            pts, v = [], base * 0.7
            for i in range(120):
                v += (base - v) * 0.03 + (rnd.random() - 0.45) * base * 0.02
                pts.append(round(max(v, base * 0.2), 0))
            pts[-1] = round(base, 0)
            return self._send(200, json.dumps({"ca": ca, "points": pts}).encode())
        return self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        ln = int(self.headers.get("Content-Length", "0") or 0)
        try:
            payload = json.loads(self.rfile.read(ln).decode() or "{}")
        except Exception:
            payload = {}
        if u.path == "/api/buy":
            ca = str(payload.get("ca", ""))
            chain = str(payload.get("chain", "solana"))
            try:
                from src.scorer import TokenFeatures, ScoreResult
                from src.executor.buyer import execute_buy
                t = TokenFeatures(ca=ca, chain=chain)
                r = ScoreResult(decision="BUY", score=0.0)
                res = execute_buy(t, r, float(payload.get("price", 1.0) or 1.0), CFG)
                return self._send(200, json.dumps({"ok": True, **res}).encode())
            except Exception as e:
                return self._send(500, json.dumps({"ok": False, "error": str(e)[:300]}).encode())
        if u.path == "/api/close":
            ca = str(payload.get("ca", ""))
            chain = str(payload.get("chain", "solana"))
            m = live_market(chain, ca)
            if not m or not m.get("price"):
                return self._send(200, json.dumps(
                    {"ok": False, "error": "harga live tak tersedia"}).encode())
            want = payload.get("qty")
            try:
                con = db_con(self.db_path)
                con.execute(
                    "INSERT INTO trades(ca,chain,side,amount_sol,price,ts,note)"
                    " VALUES(?,?,?,?,?,datetime('now'),?)",
                    (ca, chain, "SELL", 0.0, float(m["price"]),
                     f"CLOSE qty={want} @ {m['price']}" if want else
                     f"CLOSE-ALL @ {m['price']}"))
                con.commit()
                con.close()
            except Exception as e:
                return self._send(500, json.dumps({"ok": False, "error": str(e)[:200]}).encode())
            return self._send(200, json.dumps(
                {"ok": True, "price": m["price"]}).encode())
        if u.path == "/api/reset":
            try:
                con = db_con(self.db_path)
                con.execute("delete from trades")
                con.commit()
                con.close()
            except Exception as e:
                return self._send(500, json.dumps({"ok": False, "error": str(e)[:200]}).encode())
            return self._send(200, json.dumps({"ok": True}).encode())
        return self._send(404, b'{"error":"not found"}')

    def log_message(self, *a):
        pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--db", default="./degen.db")
    a = ap.parse_args()
    Handler.db_path = a.db
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"dashboard http://localhost:{a.port}/ db={a.db}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()

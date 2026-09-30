"""Dashboard server (stdlib only): serve index.html + JSON API dari degen.db.

Run:
  python dashboard/server.py --port 8080 --db ./degen.db
Buka: http://localhost:8080/
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from src.config import load_config
from src.positions import build_positions, live_market, trade_history

INDEX = HERE / "index.html"
CFG = load_config(str(ROOT / "config.yaml"))


def db_con(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def safe_sym(s: str) -> str:
    return str(s or "?").encode("ascii", "ignore").decode() or "?"


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
            return self._send(200, json.dumps(build_positions(self.db_path, CFG)).encode())
        if u.path == "/api/history":
            try:
                lim = int((q.get("limit", ["200"])[0] or 200))
            except Exception:
                lim = 200
            return self._send(200, json.dumps(trade_history(self.db_path, lim)).encode())
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
                from src.positions import record_sell
                q = float(want) if want else 0.0
                if q <= 0:
                    from src.positions import apply_fifo, load_trade_rows
                    lots, _ = apply_fifo(load_trade_rows(self.db_path))
                    q = sum(x[0] for x in lots.get((chain, ca), []))
                record_sell(self.db_path, ca, chain, q, float(m["price"]), "CLOSE")
            except Exception as e:
                return self._send(500, json.dumps({"ok": False, "error": str(e)[:200]}).encode())
            return self._send(200, json.dumps(
                {"ok": True, "price": m["price"]}).encode())
        if u.path == "/api/reset":
            try:
                con = db_con(self.db_path)
                con.execute("delete from trades")
                try:
                    con.execute("delete from paper_state")
                except Exception:
                    pass
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

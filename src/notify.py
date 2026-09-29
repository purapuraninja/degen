"""Notifikasi: console + Telegram opsional (tanpa deps tambahan)."""
from __future__ import annotations
import os
import urllib.request
import urllib.parse

def notify_console(msg: str) -> None:
    print(msg, flush=True)

def notify_telegram(msg: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat, "text": msg[:4000]}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"[notify-telegram-gagal] {e}", flush=True)
        return False

def notify(msg: str) -> None:
    notify_console(msg)
    notify_telegram(msg)

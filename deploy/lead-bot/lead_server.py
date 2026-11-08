#!/usr/bin/env python3
"""Приём заявок с формы lamon.school → мессенджер.

POST /api/lead  {"name": "...", "phone": "+7 (XXX) XXX-XX-XX"}
Пишет каждую заявку в JSONL-лог и шлёт уведомление ботом:
  • MAX      — MAX_BOT_TOKEN + MAX_USER_ID   (api: platform-api2.max.ru, доступен из России)
  • Telegram — TG_BOT_TOKEN + TG_CHAT_ID     (api.telegram.org; с российских серверов часто недоступен)
Настроенные каналы используются все; достаточно одного.
Конфиг: /etc/lamon/lead.env. Только стандартная библиотека.

Узнать свой MAX user_id (после того как написали боту):  python3 lead_server.py --find-max-user
"""
import json, os, re, time, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import defaultdict, deque

TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")
MAX_TOKEN = os.environ.get("MAX_BOT_TOKEN", "")
MAX_USER_ID = os.environ.get("MAX_USER_ID", "")
MAX_API = "https://platform-api2.max.ru"
LOG = os.environ.get("LEAD_LOG", "/var/lib/lamon/leads.jsonl")
PORT = int(os.environ.get("LISTEN_PORT", "8081"))

_hits = defaultdict(deque)  # простая защита от флуда: не больше 5 заявок с IP за 10 минут


def too_many(ip: str) -> bool:
    q = _hits[ip]; now = time.time()
    while q and now - q[0] > 600:
        q.popleft()
    q.append(now)
    return len(q) > 5


def tg_send(text: str) -> bool:
    if not TOKEN or not CHAT_ID:
        return False
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception as e:  # noqa: BLE001
        print("telegram error:", e, flush=True)
        return False


def max_send(text: str) -> bool:
    if not MAX_TOKEN or not MAX_USER_ID:
        return False
    body = json.dumps({"text": text, "format": "markdown"}).encode()
    req = urllib.request.Request(f"{MAX_API}/messages?user_id={urllib.parse.quote(MAX_USER_ID)}", data=body, method="POST",
                                 headers={"Authorization": MAX_TOKEN, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception as e:  # noqa: BLE001
        print("max error:", e, flush=True)
        return False


def max_find_user() -> None:
    """Печатает user_id всех, кто писал боту (по последним обновлениям)."""
    req = urllib.request.Request(f"{MAX_API}/updates?limit=50", headers={"Authorization": MAX_TOKEN})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.load(r)
    seen = {}
    for u in data.get("updates", []):
        sender = (u.get("message") or {}).get("sender") or u.get("user") or {}
        if sender.get("user_id"):
            seen[sender["user_id"]] = f"{sender.get('first_name','')} {sender.get('last_name') or ''} @{sender.get('username') or '-'}".strip()
    for uid, who in seen.items():
        print(uid, who)
    if not seen:
        print("Обновлений нет: напишите боту любое сообщение в MAX и повторите.")


def notify(text_html: str, text_md: str) -> dict:
    return {"telegram": tg_send(text_html), "max": max_send(text_md)}


class H(BaseHTTPRequestHandler):
    server_version = "lamon-lead/1.0"

    def _json(self, code: int, obj: dict):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/lead/health":
            return self._json(200, {"ok": True, "telegram": bool(TOKEN and CHAT_ID), "max": bool(MAX_TOKEN and MAX_USER_ID)})
        self._json(404, {"ok": False})

    def do_POST(self):
        if self.path != "/api/lead":
            return self._json(404, {"ok": False})
        ip = self.headers.get("X-Real-IP") or self.client_address[0]
        if too_many(ip):
            return self._json(429, {"ok": False, "error": "Слишком много заявок. Попробуйте позже."})
        try:
            n = min(int(self.headers.get("Content-Length", "0")), 4096)
            payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception:  # noqa: BLE001
            return self._json(400, {"ok": False, "error": "Некорректный запрос."})
        name = str(payload.get("name", "")).strip()[:80]
        phone = str(payload.get("phone", "")).strip()[:32]
        digits = re.sub(r"\D", "", phone)
        if not name or len(digits) != 11:
            return self._json(400, {"ok": False, "error": "Нужны имя и полный номер телефона."})
        honeypot = str(payload.get("site", "")).strip()
        if honeypot:  # поле, которое человек не заполняет
            return self._json(200, {"ok": True})
        rec = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "name": name, "phone": phone, "ip": ip,
               "ua": self.headers.get("User-Agent", "")[:160], "page": self.headers.get("Referer", "")[:200]}
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        sent = notify(
            f"<b>Заявка на звонок</b>\nИмя: {name}\nТелефон: <code>{phone}</code>\nВремя: {rec['ts']}",
            f"**Заявка на звонок**\nИмя: {name}\nТелефон: `{phone}`\nВремя: {rec['ts']}",
        )
        print("lead:", rec, "sent:", sent, flush=True)
        self._json(200, {"ok": True, **sent})

    def log_message(self, *_):  # тише в journal
        pass


if __name__ == "__main__":
    import sys
    if "--find-max-user" in sys.argv:
        max_find_user(); sys.exit(0)
    print(f"lamon-lead on 127.0.0.1:{PORT}, telegram: {bool(TOKEN and CHAT_ID)}, max: {bool(MAX_TOKEN and MAX_USER_ID)}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()

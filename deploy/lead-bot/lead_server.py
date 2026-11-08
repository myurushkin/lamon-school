#!/usr/bin/env python3
"""Приём заявок с формы lamon.school → Telegram.

POST /api/lead  {"name": "...", "phone": "+7 (XXX) XXX-XX-XX"}
Пишет каждую заявку в JSONL-лог и шлёт сообщение в Telegram через бота.
Конфиг: /etc/lamon/lead.env  (TG_BOT_TOKEN, TG_CHAT_ID, LEAD_LOG, LISTEN_PORT)
Только стандартная библиотека.
"""
import json, os, re, time, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import defaultdict, deque

TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")
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
            return self._json(200, {"ok": True, "telegram": bool(TOKEN and CHAT_ID)})
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
        sent = tg_send(
            f"<b>Заявка на звонок</b>\n"
            f"Имя: {name}\n"
            f"Телефон: <code>{phone}</code>\n"
            f"Время: {rec['ts']}"
        )
        print("lead:", rec, "telegram:", sent, flush=True)
        self._json(200, {"ok": True, "telegram": sent})

    def log_message(self, *_):  # тише в journal
        pass


if __name__ == "__main__":
    print(f"lamon-lead on 127.0.0.1:{PORT}, telegram configured: {bool(TOKEN and CHAT_ID)}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()

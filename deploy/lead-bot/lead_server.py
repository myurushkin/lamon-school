#!/usr/bin/env python3
"""Приём заявок с формы lamon.school → мессенджер.

POST /api/lead  {"name": "...", "phone": "+7 (XXX) XXX-XX-XX"}
Пишет каждую заявку в JSONL-лог и шлёт уведомление ботом:
  • MAX      — MAX_BOT_TOKEN + MAX_USER_ID   (api: botapi.max.ru, доступен из России)
  • Telegram — TG_BOT_TOKEN + TG_CHAT_ID     (api.telegram.org; с российских серверов часто недоступен)
Настроенные каналы используются все; достаточно одного.
Конфиг: /etc/lamon/lead.env. Только стандартная библиотека.

Узнать свой MAX user_id (после того как написали боту):  python3 lead_server.py --find-max-user
"""
import html
import http.client
import socket
import ssl
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import json, os, re, time, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import defaultdict, deque

TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")
MAX_TOKEN = os.environ.get("MAX_BOT_TOKEN", "")
MAX_USER_ID = os.environ.get("MAX_USER_ID", "")
MAX_API = "https://botapi.max.ru"
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER)
MAIL_TO = [x.strip() for x in os.environ.get("MAIL_TO", "").split(",") if x.strip()]
LOG = os.environ.get("LEAD_LOG", "/var/lib/lamon/leads.jsonl")
PORT = int(os.environ.get("LISTEN_PORT", "8081"))

_hits = defaultdict(deque)  # простая защита от флуда: не больше 5 заявок с IP за 10 минут


def too_many(ip: str) -> bool:
    q = _hits[ip]; now = time.time()
    while q and now - q[0] > 600:
        q.popleft()
    q.append(now)
    return len(q) > 5


TG_API_IPS = [x for x in os.environ.get("TG_API_IPS", "149.154.167.220,149.154.167.99,149.154.166.110").split(",") if x]
TG_HOST = "api.telegram.org"
TG_PROXY_URL = os.environ.get("TG_PROXY_URL", "").rstrip("/")
TG_PROXY_KEY = os.environ.get("TG_PROXY_KEY", "")


class _PinnedHTTPS(http.client.HTTPSConnection):
    """HTTPS к заданному IP с SNI/проверкой сертификата по настоящему имени хоста."""

    def __init__(self, ip: str, **kw):
        super().__init__(ip, 443, **kw)
        self._sni = TG_HOST

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self._sni)


def tg_api(method: str, params: dict) -> dict | None:
    """Вызов Bot API: сначала по DNS, затем по запасным IP (с российских серверов часть адресов недоступна)."""
    if not TOKEN:
        return None
    body = urllib.parse.urlencode(params).encode()
    path = f"/bot{TOKEN}/{method}"
    hdr = {"Content-Type": "application/x-www-form-urlencoded", "Host": TG_HOST}
    ctx = ssl.create_default_context()
    if TG_PROXY_URL and TG_PROXY_KEY:
        try:
            req = urllib.request.Request(TG_PROXY_URL + path, data=body, method="POST",
                                         headers={**hdr, "Host": TG_PROXY_URL.split("//", 1)[1], "x-proxy-key": TG_PROXY_KEY})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode() or "{}")
                if data.get("ok"):
                    return data
                print(f"telegram {method} via proxy: {data.get('description', '')}", flush=True)
                return None
        except urllib.error.HTTPError as e:
            print(f"telegram {method} via proxy: HTTP {e.code}", flush=True)
            if e.code in (400, 401, 403, 404):
                return None
        except Exception as e:  # noqa: BLE001
            print(f"telegram {method} via proxy: {e}", flush=True)
    attempts = [None] + TG_API_IPS
    for ip in attempts:
        try:
            conn = http.client.HTTPSConnection(TG_HOST, timeout=6, context=ctx) if ip is None else _PinnedHTTPS(ip, timeout=6, context=ctx)
            conn.request("POST", path, body=body, headers=hdr)
            r = conn.getresponse()
            data = json.loads(r.read().decode() or "{}")
            conn.close()
            if r.status == 200 and data.get("ok"):
                return data
            print(f"telegram {method} via {ip or 'dns'}: HTTP {r.status} {data.get('description', '')}", flush=True)
            if r.status in (400, 401, 403, 404):
                return None  # ошибка запроса, а не сети — другие адреса не помогут
        except Exception as e:  # noqa: BLE001
            print(f"telegram {method} via {ip or 'dns'}: {e}", flush=True)
    return None


def tg_send(text: str) -> bool:
    if not TOKEN or not CHAT_ID:
        return False
    return tg_api("sendMessage", {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}) is not None


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


def mail_send(subject: str, text: str) -> bool:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and MAIL_TO):
        return False
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("Lamon заявки", MAIL_FROM))
    msg["To"] = ", ".join(MAIL_TO)
    msg.set_content(text)
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:  # noqa: BLE001
        print("mail error:", e, flush=True)
        return False


def notify(text_html: str, text_md: str, plain: str = "", subject: str = "Новая заявка на lamon.school") -> dict:
    return {"telegram": tg_send(text_html), "max": max_send(text_md), "mail": mail_send(subject, plain or text_md)}


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
            return self._json(200, {"ok": True, "telegram": bool(TOKEN and CHAT_ID), "max": bool(MAX_TOKEN and MAX_USER_ID), "mail": bool(SMTP_HOST and SMTP_USER and SMTP_PASS and MAIL_TO)})
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
        source = re.sub(r"[^\w\-]", "", str(payload.get("source", "")))[:40]
        role = str(payload.get("role", "")).strip()[:40]
        about = str(payload.get("about", "")).strip()[:1000]
        digits = re.sub(r"\D", "", phone)
        if not name or len(digits) != 11:
            return self._json(400, {"ok": False, "error": "Нужны имя и полный номер телефона."})
        honeypot = str(payload.get("site", "")).strip()
        if honeypot:  # поле, которое человек не заполняет
            return self._json(200, {"ok": True})
        rec = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "name": name, "phone": phone, "source": source, "role": role, "about": about, "ip": ip,
               "ua": self.headers.get("User-Agent", "")[:160], "page": self.headers.get("Referer", "")[:200]}
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        sent = notify(
            f"<b>Заявка</b> · {source or 'main'}{' · '+role if role else ''}\nИмя: {name}\nТелефон: <code>{phone}</code>{chr(10)+'О ситуации: '+html.escape(about) if about else ''}\nВремя: {rec['ts']}",
            f"**Заявка** · {source or 'main'}{' · '+role if role else ''}\nИмя: {name}\nТелефон: `{phone}`{chr(10)+'О ситуации: '+about if about else ''}\nВремя: {rec['ts']}",
            plain=f"Имя: {name}\nТелефон: {phone}\nЛендинг: {source or 'main'}{chr(10)+'Роль: '+role if role else ''}{chr(10)+chr(10)+'О ситуации:'+chr(10)+about if about else ''}\n\nВремя: {rec['ts']}\nСтраница: {rec['page']}",
            subject=f"Заявка lamon.school: {name}, {phone}",
        )
        print("lead:", rec, "sent:", sent, flush=True)
        self._json(200, {"ok": True, **sent})

    def log_message(self, *_):  # тише в journal
        pass


if __name__ == "__main__":
    import sys
    if "--find-max-user" in sys.argv:
        max_find_user(); sys.exit(0)
    if "--test-mail" in sys.argv:
        print("mail:", mail_send("Проверка: заявки lamon.school", "Письма с заявками подключены. Это тестовое сообщение.")); sys.exit(0)
    print(f"lamon-lead on 127.0.0.1:{PORT}, telegram: {bool(TOKEN and CHAT_ID)}, max: {bool(MAX_TOKEN and MAX_USER_ID)}, mail: {bool(SMTP_HOST and SMTP_USER and SMTP_PASS and MAIL_TO)}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()

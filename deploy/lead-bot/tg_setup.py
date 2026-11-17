#!/usr/bin/env python3
"""Привязка Telegram-бота к приёмнику заявок.

Запуск на сервере: sudo /opt/lamon/tg_setup.py
Читает TG_BOT_TOKEN из /etc/lamon/lead.env, находит chat_id по последнему
сообщению боту (нужно написать боту /start), записывает TG_CHAT_ID в env,
перезапускает сервис и шлёт тестовое сообщение. Токен на экран не выводит.
"""
import os, re, subprocess, sys

ENV = "/etc/lamon/lead.env"
env = {}
for line in open(ENV, encoding="utf-8"):
    m = re.match(r"^([A-Z_]+)=(.*)$", line.strip())
    if m:
        env[m.group(1)] = m.group(2)
token = env.get("TG_BOT_TOKEN", "")
if not token:
    sys.exit(f"TG_BOT_TOKEN пуст в {ENV}")
os.environ["TG_BOT_TOKEN"] = token
sys.path.insert(0, "/opt/lamon")
import lead_server as ls  # noqa: E402

me = ls.tg_api("getMe", {})
if not me:
    sys.exit("Telegram не отвечает или токен неверный, см. вывод выше")
print("бот:", "@" + me["result"]["username"])
upd = ls.tg_api("getUpdates", {"limit": 100}) or {"result": []}
chats = [u["message"]["chat"] for u in upd["result"] if "message" in u]
if not chats:
    sys.exit("Боту ещё никто не писал. Отправь ему /start в Telegram и запусти снова.")
chat = chats[-1]
chat_id = str(chat["id"])
print("chat_id:", chat_id, "(", chat.get("first_name", ""), chat.get("username", ""), ")")
text = open(ENV, encoding="utf-8").read()
text = re.sub(r"^TG_CHAT_ID=.*$", f"TG_CHAT_ID={chat_id}", text, flags=re.M) if re.search(r"^TG_CHAT_ID=", text, re.M) else text + f"\nTG_CHAT_ID={chat_id}\n"
open(ENV, "w", encoding="utf-8").write(text)
subprocess.run(["systemctl", "restart", "lamon-lead"], check=True)
ls.CHAT_ID = chat_id
ok = ls.tg_send("Lamon: уведомления о заявках подключены ✅")
print("тестовое сообщение:", "отправлено" if ok else "НЕ отправлено")

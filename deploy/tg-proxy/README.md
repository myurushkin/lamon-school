# Прокси к Telegram через Cloudflare Worker

С сервера 194.113.35.217 api.telegram.org недоступен (хостер блокирует), а Cloudflare доступен.
Worker принимает запросы с секретным заголовком `x-proxy-key` и пересылает их в Telegram.

## Деплой (dash.cloudflare.com → Workers & Pages → Create → Start with Hello World)
1. Имя `lamon-tg-proxy`, вставить содержимое `worker.js`, Deploy.
2. Settings → Variables and Secrets → Add → type Secret, name `PROXY_KEY`, значение — длинная случайная строка
   (например `python3 -c "import secrets;print(secrets.token_urlsafe(32))"`).
3. Убедиться, что включён workers.dev route: `https://lamon-tg-proxy.<subdomain>.workers.dev`.

## На сервере
В `/etc/lamon/lead.env` добавить:
```
TG_PROXY_URL=https://lamon-tg-proxy.<subdomain>.workers.dev
TG_PROXY_KEY=<тот же секрет>
```
и `sudo /opt/lamon/tg_setup.py`. Приёмник пробует прокси первым, затем прямые адреса Telegram.

#!/usr/bin/env bash
# Установка сервиса заявок на сервере. Запускать на сервере: bash ~/deploy/setup-lead-bot.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
sudo mkdir -p /opt/lamon /etc/lamon /var/lib/lamon
sudo cp "$HERE/lead-bot/lead_server.py" /opt/lamon/lead_server.py
sudo chown -R lending:lending /var/lib/lamon
if [ ! -f /etc/lamon/lead.env ]; then
  sudo cp "$HERE/lead-bot/lead.env.example" /etc/lamon/lead.env
  echo "!! Заполните /etc/lamon/lead.env (TG_BOT_TOKEN, TG_CHAT_ID)"
fi
sudo chown lending:lending /etc/lamon/lead.env && sudo chmod 600 /etc/lamon/lead.env
sudo cp "$HERE/lead-bot/lamon-lead.service" /etc/systemd/system/lamon-lead.service
sudo systemctl daemon-reload
sudo systemctl enable --now lamon-lead
sudo systemctl restart lamon-lead
sleep 1; systemctl is-active lamon-lead && curl -s http://127.0.0.1:8081/api/lead/health; echo

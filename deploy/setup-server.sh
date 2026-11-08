#!/usr/bin/env bash
# Разовая настройка сервера (Ubuntu 24.04). Запускать на сервере под пользователем с sudo:
#   bash setup-server.sh <deploy_user> "<deploy_public_key>"
set -euo pipefail
DEPLOY_USER="${1:-lending}"
DEPLOY_PUBKEY="${2:-}"
SITE_DIR=/var/www/lamon

sudo apt-get update -qq
sudo apt-get install -y -qq nginx rsync ufw

# каталог сайта принадлежит деплой-пользователю, чтобы rsync из CI писал без sudo
sudo mkdir -p "$SITE_DIR"
sudo chown -R "$DEPLOY_USER":"$DEPLOY_USER" "$SITE_DIR"

# ключ для CI
if [ -n "$DEPLOY_PUBKEY" ]; then
  sudo -u "$DEPLOY_USER" mkdir -p "/home/$DEPLOY_USER/.ssh"
  sudo -u "$DEPLOY_USER" bash -c "grep -qF '$DEPLOY_PUBKEY' ~/.ssh/authorized_keys 2>/dev/null || echo '$DEPLOY_PUBKEY' >> ~/.ssh/authorized_keys"
  sudo chmod 700 "/home/$DEPLOY_USER/.ssh"; sudo chmod 600 "/home/$DEPLOY_USER/.ssh/authorized_keys"
fi

# nginx
sudo cp "$(dirname "$0")/nginx.conf" /etc/nginx/sites-available/lamon
sudo ln -sf /etc/nginx/sites-available/lamon /etc/nginx/sites-enabled/lamon
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
sudo systemctl enable nginx

# файрвол: ssh + http/https
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "Готово. Сайт отдаётся из $SITE_DIR. HTTPS после привязки домена:"
echo "  sudo apt-get install -y certbot python3-certbot-nginx && sudo certbot --nginx -d lamon.school -d www.lamon.school"

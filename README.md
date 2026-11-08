# lamon.school

Сайт школы Lamon. Astro 7, статическая сборка.

## Локально

```bash
npm install
npm run dev        # http://127.0.0.1:4321
npm run build      # dist/
npm run preview    # http://127.0.0.1:8768
```

Ключ Яндекс Карт (необязательно): `PUBLIC_YMAPS_KEY=...` в `.env`. Без него карта на Leaflet + OpenStreetMap.

## Контент

- Главная: `src/pages/index.astro`, секции в `src/components/sections/`.
- Преподаватели: `src/data/team.ts`. Публикации: `src/data/publications.ts`.
- Блог: `src/content/blog/<slug>.md`, фото в `public/images/blog/<slug>/`.
  Запись с `featured: true` показывается на главной как кейс.
- Импорт фото из `~/shared/school`: `node scripts/import-photos.mjs`.

## Деплой

Пуш в `main` → GitHub Actions собирает сайт и заливает `dist/` по SSH в `/var/www/lamon`, nginx отдаёт статику.

Секреты репозитория (Settings → Secrets and variables → Actions):

| Секрет | Значение |
|---|---|
| `DEPLOY_HOST` | `194.113.35.217` |
| `DEPLOY_USER` | `lending` |
| `DEPLOY_PATH` | `/var/www/lamon` |
| `DEPLOY_SSH_KEY` | приватный ключ деплоя (пара к ключу в `authorized_keys` на сервере) |
| `PUBLIC_YMAPS_KEY` | ключ Яндекс Карт, можно не задавать |

Разовая настройка сервера: скопировать папку `deploy/` на сервер и выполнить
`bash deploy/setup-server.sh lending "<публичный ключ деплоя>"` под пользователем с sudo.

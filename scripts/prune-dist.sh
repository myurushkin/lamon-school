#!/usr/bin/env sh
# Оставляет в dist/ только страницы, которые публикуем наружу.
# Список публичных страниц — PUBLIC_PAGES (каталоги внутри dist, корень всегда остаётся).
set -e
cd "$(dirname "$0")/../dist"
PUBLIC_PAGES="${PUBLIC_PAGES:-students-a}"
for d in */; do
  d="${d%/}"
  case " _astro images people partners vendor $PUBLIC_PAGES " in
    *" $d "*) ;;
    *) rm -rf "$d" ;;
  esac
done
ls

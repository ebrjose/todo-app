#!/bin/sh
set -e

# Only the web container sets DJANGO_MIGRATE=1, so migrations run once.
if [ "${DJANGO_MIGRATE:-0}" = "1" ]; then
  python manage.py migrate --noinput
fi

exec "$@"

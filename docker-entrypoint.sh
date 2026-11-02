#!/bin/sh
set -e

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py ensure_demo_user

exec gunicorn app.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --threads 8 \
    --timeout 0
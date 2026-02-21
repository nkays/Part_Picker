#!/bin/bash
set -e

cd /code

uv run python manage.py migrate

RUNTIME_PORT=${PORT:-8080}
RUNTIME_HOST=${HOST:-0.0.0.0} 

exec uv run gunicorn BuzzardBuilds.wsgi:application \
    --bind ${RUNTIME_HOST}:${RUNTIME_PORT} \
    --workers 3 \
    --log-level info
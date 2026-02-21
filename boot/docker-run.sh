#!/bin/bash
set -e

cd /code

# Run startup management commands
uv run python manage.py sendtestemail --admins
uv run python manage.py migrate
uv run python manage.py auto_admin

# Default port (Railway overrides this with PORT env var)
export RUNTIME_PORT=${PORT:-8080}
export RUNTIME_HOST=${HOST:-0.0.0.0}
# Start Gunicorn
exec uv run gunicorn BuzzardBuilds.wsgi:application --bind $RUNTIME_HOST:$RUNTIME_PORT
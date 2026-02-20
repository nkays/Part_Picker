#!/bin/bash

source /opt/venv/bin/activate
cd /code

python manage.py sendtestemail --admins
python manage.py migrate 
python manage.py auto_admin


export RUNTIME_PORT=8080

# python manage.py collectstatic --clear --noinput
gunicorn BuzzardBuilds.wsgi:application --bind 0.0.0.0:8080:$RUNTIME_PORT
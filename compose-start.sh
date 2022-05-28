#!/usr/bin/env bash
#
# This script is used to start our Django WSGI process (gunicorn in this case)
# for use with docker-compose.  In deployed or production scenarios you would
# not necessarily use this exact setup.
#
set -e
set -x

wait-for-it -h db -p 5432 -t 20

python manage.py collectstatic --noinput

make locales fixtures

newrelic-admin run-program gunicorn -c gunicorn.conf.py --log-level INFO --reload -b 0.0.0.0:${PORT:=8000} config.wsgi

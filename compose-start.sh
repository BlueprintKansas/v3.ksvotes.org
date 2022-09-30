#!/usr/bin/env bash
#
# This script is used to start our Django WSGI process (gunicorn in this case)
# for use with docker-compose.  In deployed or production scenarios you would
# not necessarily use this exact setup.
#
set -e
set -x

make migrate static locales fixtures

newrelic-admin run-program gunicorn -c gunicorn.conf.py --reload -b 0.0.0.0:${PORT:=8000} config.wsgi

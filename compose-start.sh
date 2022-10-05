#!/usr/bin/env bash
#
# This script is used to start our Django WSGI process (gunicorn in this case)
# for use with docker-compose.  In deployed or production scenarios you would
# not necessarily use this exact setup.
#
set -e
set -x

make migrate static locales fixtures

# must update $PORT from heroku at runtime
NGINX_PORT=${PORT:=8000}
sed -i -e 's/set \$PORT/# set \$PORT/g' /etc/nginx/nginx.conf
sed -i -e 's/\$PORT/'"$NGINX_PORT"'/g' /etc/nginx/nginx.conf

# start proxy first
nginx -g 'daemon on;'

# run app last
newrelic-admin run-program gunicorn -c gunicorn.conf.py --reload -b 0.0.0.0:${APP_PORT:=8001} config.wsgi

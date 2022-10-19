# -*- coding: utf-8 -*-
# vim: ft=python
# pylint: disable=missing-docstring, line-too-long, invalid-name
import os
from psycogreen.gevent import patch_psycopg  # use this if you use gevent workers


BASE_DIR = os.environ["H"] if os.environ.get("H", None) else "/code"

accesslog = "-"
capture_output = True
bind = "unix:/run/gunicorn.sock"
loglevel = "INFO"
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "gevent"
keepalive = 32
worker_connections = 10000
max_requests = 10000

pythonpath = BASE_DIR
chdir = BASE_DIR


def post_fork(server, worker):
    from gevent import monkey

    patch_psycopg()
    worker.log.info("Made Psycopg2 Green")
    monkey.patch_all()

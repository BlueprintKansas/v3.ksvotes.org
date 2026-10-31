# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.db import connections
from django.conf import settings
import redis
import logging
import time

logger = logging.getLogger(__name__)


def check_db(connection):
    db_name = connection.settings_dict["NAME"]
    try:
        db_start = time.time()
        connection.ensure_connection()
        db_ok = connection.is_usable()
        db_response_time = time.time() - db_start
    except Exception as err:  # pragma: no cover
        logger.exception(err)
        db_ok = False
        db_response_time = 0
    logger.debug(f"{db_name=} {db_ok=} {db_response_time=}")

    return db_ok


def health_check(request):
    db_ok = all(check_db(conn) for conn in connections.all())
    logger.debug(f"{db_ok=}")

    # Check cache connection
    cache_ok = False
    try:
        redis_client = redis.from_url(settings.CACHES["default"]["LOCATION"])
        cache_ok = redis_client.ping()
    except (redis.exceptions.RedisError, KeyError):
        pass

    logger.debug(f"{cache_ok=}")

    status = db_ok and cache_ok
    status_code = 200 if status else 503
    return JsonResponse({"status": "ok" if status else "unhealthy"}, status=status_code)

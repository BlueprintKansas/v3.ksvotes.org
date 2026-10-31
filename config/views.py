# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.db import connections
from django.conf import settings
import redis


def health_check(request):
    # Check database connections
    db_ok = all(conn.cursor().execute("SELECT 1") for conn in connections.all())

    # Check cache connection
    cache_ok = False
    try:
        redis_client = redis.from_url(settings.CACHES["default"]["LOCATION"])
        cache_ok = redis_client.ping()
    except (redis.exceptions.RedisError, KeyError):
        pass

    status = db_ok and cache_ok
    status_code = 200 if status else 503
    return JsonResponse({"status": "ok" if status else "unhealthy"}, status=status_code)

# -*- coding: utf-8 -*-
from redis import WatchError
import redis
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class KSVotesRedis:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URL, **settings.CACHES["default"]["OPTIONS"]
        )
        self.namespace = settings.APP_CONFIG

    def get(self, key):
        return self.redis_client.get(self.namespace + ":" + key)

    def set(self, key, value, ttl=60):
        return self.redis_client.set(self.namespace + ":" + key, value, ex=ttl)

    def clear(self, key):
        return self.redis_client.delete(self.namespace + ":" + key)

    def get_or_set(self, key, setter, ttl):
        ns_key = self.namespace + ":" + key
        with self.redis_client.pipeline() as pipe:
            try:
                pipe.watch(ns_key)
                # after WATCHing, the pipeline is put into immediate execution
                # mode until we tell it to start buffering commands again.
                # this allows us to get the current value of our sequence
                if pipe.exists(ns_key):
                    return pipe.get(ns_key)
                # now we can put the pipeline back into buffered mode with MULTI
                pipe.multi()
                pipe.set(ns_key, setter(), ex=ttl)
                pipe.get(ns_key)
                # and finally, execute the pipeline (the set and get commands)
                return pipe.execute()[-1]
                # if a WatchError wasn't raised during execution, everything
                # we just did happened atomically.
            except WatchError:
                # another client must have changed key between
                # the time we started WATCHing it and the pipeline's execution.
                # Let's just get the value they changed it to.
                return pipe.get(ns_key)

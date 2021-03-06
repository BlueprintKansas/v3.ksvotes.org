# -*- coding: utf-8 -*-
from ksvotes.services.ksvotes_redis import KSVotesRedis
from airtable import Airtable
import os
import json


class EarlyVotingLocations:
    def __init__(self, county):
        self.locations = None

        # disabled w/o this env var set
        if not os.getenv("AIRTABLE_EV_TABLE"):
            return

        self.county = county

        # look first in redis cache
        self.locations = self.get_cached_locations()

        # otherwise fetch and cache
        if not self.locations:
            self.locations = self.fetch_locations()

    def cache_key(self):
        return "ev2-{}".format(self.county)

    def get_cached_locations(self):
        redis = KSVotesRedis()
        locations = redis.get(self.cache_key())
        if locations:
            return json.loads(locations)
        else:
            return None

    def fetch_locations(self):
        redis = KSVotesRedis()
        airtable = Airtable(
            os.getenv("AIRTABLE_EV_BASE_ID"),
            os.getenv("AIRTABLE_EV_TABLE"),
            os.getenv("AIRTABLE_EV_KEY"),
        )
        response = airtable.get_all(
            formula="AND( COUNTY = '{}' )".format(self.county.upper())
        )

        if response is None or len(response) == 0:
            return

        # some counties do not have actual locations
        if "LOCATION" not in response[0]["fields"]:
            return

        locations = []
        for loc in response:
            evl = {"location": loc["fields"]["LOCATION"], "hours": []}
            for field, value in loc["fields"].items():
                if "DAY" in field:
                    evl["hours"].append({"day": field, "time": value})

            locations.append(evl)

        redis.set(
            self.cache_key(),
            json.dumps(locations).encode(),
            os.getenv("EVL_TTL", "3600"),
        )
        return locations

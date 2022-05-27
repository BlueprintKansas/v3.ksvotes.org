# -*- coding: utf-8 -*-
from test_plus import TestCase
from django.utils import timezone
import uuid
from ksvotes.models import Registrant
from ksvotes.services.ksvotes_redis import KSVotesRedis


class ApiTestCase(TestCase):
    def test_api_total_processed(self):
        redis = KSVotesRedis()

        # We should be empty at first
        response = self.client.get("/api/total-processed/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["registrations"], 0)
        self.assertEqual(payload["advanced_ballots"], 0)

        redis.clear("vr-total-processed")
        redis.clear("ab-total-processed")

        now = timezone.now()

        new_registrant = Registrant(lang="en", county="Johnson", vr_completed_at=now)
        new_registrant.save()

        # We should have a single registrant now
        response = self.client.get("/api/total-processed/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["registrations"], 1)
        self.assertEqual(payload["advanced_ballots"], 0)

        redis.clear("vr-total-processed")
        redis.clear("ab-total-processed")

        second_registrant = Registrant(
            lang="en",
            county="Johnson",
            ab_completed_at=now,
            session_id=uuid.uuid4(),
        )
        second_registrant.save()

        # We should have a second registrant now
        response = self.client.get("/api/total-processed/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["registrations"], 1)
        self.assertEqual(payload["advanced_ballots"], 1)

        redis.clear("vr-total-processed")
        redis.clear("ab-total-processed")

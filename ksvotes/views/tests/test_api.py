# -*- coding: utf-8 -*-
from ksvotes.tests.test_utils import KSVotesTestCase
from django.utils import timezone
from django.conf import settings
import uuid
from ksvotes.models import Registrant
from ksvotes.services.ksvotes_redis import KSVotesRedis
from ksvotes.services.registrant_stats import RegistrantStats


class ApiTestCase(KSVotesTestCase):
    def setUp(self):
        # make sure demo does NOT exist
        Registrant.find_by_session(settings.DEMO_UUID).delete()

    def test_api_total_processed(self):
        redis = KSVotesRedis()
        redis.clear("vr-total-processed")
        redis.clear("ab-total-processed")

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
        s = RegistrantStats()
        self.assertEqual(s.vr_total_processed(), 1)

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

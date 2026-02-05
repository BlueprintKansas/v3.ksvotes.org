# -*- coding: utf-8 -*-
from ksvotes.utils import zip_code_matches, parse_election_date
from datetime import datetime
from test_plus import TestCase
from django.conf import settings


class KSVotesTestCase(TestCase):
    def update_session(self, registrant):
        session = self.client.session
        session["id"] = str(registrant.session_id)
        session.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key
        return session

    def test_zip_code_matches(self):
        sosrec = {"Address": "123 Main St #456 Wichita, KS, 12345-9999"}

        self.assertTrue(zip_code_matches(sosrec, 12345))
        self.assertTrue(zip_code_matches(sosrec, "12345"))
        self.assertFalse(zip_code_matches(sosrec, 98765))
        self.assertFalse(zip_code_matches(sosrec, 9999))
        self.assertFalse(zip_code_matches(sosrec, "myzip"))

    def test_parse_election_date(self):
        dates = {
            "Presidential Preference Primary (March 19, 2024)": datetime(2024, 3, 19),
            "General (November 5, 2024)": datetime(2024, 11, 5),
            "Special Election (March 3, 2026)": datetime(2026, 3, 3),
            "Elecciones Especiales (3 de Marzo de 2026)": datetime(2026, 3, 3),
        }
        for election, dt in dates.items():
            d = parse_election_date(election)
            self.assertEqual(dt, d, f"parsed {election}")

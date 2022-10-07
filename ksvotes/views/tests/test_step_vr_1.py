# -*- coding: utf-8 -*-
from ksvotes.tests.test_utils import KSVotesTestCase
from ksvotes.models import Registrant
import json


class StepVR1TestCase(KSVotesTestCase):
    def create_registrant(self):
        registrant = Registrant(
            registration=json.dumps(
                {
                    "name_first": "foo",
                    "name_last": "bar",
                    "dob": "01/01/2000",
                    "email": "foo@example.com",
                }
            ),
            county="TEST",
            reg_lookup_complete=True,
        )
        registrant.save()
        self.update_session(registrant)
        return registrant

    def test_citizenship_not_checked_does_not_return_redirect(self):
        """
        An existing user tries to update their record, but does not select the citizen checkbox
        """
        registrant = self.create_registrant()
        form_payload = {}
        response = self.client.post("/vr/citizenship/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertFalse(registrant.is_citizen)

    def test_citizenship_checked_returns_redirect(self):
        registrant = self.create_registrant()
        form_payload = {"is_citizen": True}
        response = self.client.post("/vr/citizenship/", data=form_payload)
        self.assertRedirects(response, "/vr/name/", status_code=302)
        registrant.refresh_from_db()
        self.assertTrue(registrant.is_citizen)
        self.assertFalse(registrant.is_eighteen)

    def test_citizenship_is_eighteen_checked_returns_redirect(self):
        registrant = self.create_registrant()
        form_payload = {
            "is_citizen": True,
            "is_eighteen": "True",
        }  # test string is coerced
        response = self.client.post("/vr/citizenship/", data=form_payload)
        self.assertRedirects(response, "/vr/name/", status_code=302)
        registrant.refresh_from_db()
        self.assertTrue(registrant.is_citizen)
        self.assertTrue(registrant.is_eighteen)

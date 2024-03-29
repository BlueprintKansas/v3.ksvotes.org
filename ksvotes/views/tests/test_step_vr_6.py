# -*- coding: utf-8 -*-
from ksvotes.views.vr.example_form import signature_img_string
from ksvotes.tests.test_utils import KSVotesTestCase
from ksvotes.models import Registrant
import json


class StepVR6TestCase(KSVotesTestCase):
    def create_registrant(self):
        registrant = Registrant(
            registration=json.dumps(
                {
                    "name_first": "foo",
                    "name_last": "bar",
                    "dob": "01/01/2000",
                    "email": "foo@example.com",
                    "addr": "707 Vermont St",
                    "unit": "Room A",
                    "city": "Lawrence",
                    "state": "KANSAS",
                    "zip": "66044",
                    "identification": "nnnnn",
                }
            ),
            county="TEST",
            reg_lookup_complete=True,
            addr_lookup_complete=True,
            is_citizen=True,
            party="unaffiliated",
        )
        registrant.save()
        self.update_session(registrant)
        return registrant

    def test_vr_6_no_signature_provided(self):
        registrant = self.create_registrant()
        form_payload = {}
        response = self.client.post("/vr/preview/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertFalse(registrant.try_value("signature_string"))

    def test_vr_6_bad_signature_provided(self):
        registrant = self.create_registrant()
        form_payload = {"signature_string": "foobar"}
        response = self.client.post("/vr/preview/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertFalse(registrant.try_value("signature_string"))

    def test_valid_vr_6_returns_redirect(self):
        registrant = self.create_registrant()
        form_payload = {"signature_string": signature_img_string}
        response = self.client.post("/vr/preview/", data=form_payload)
        self.assertRedirects(response, "/vr/affirmation/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("signature_string"), signature_img_string)

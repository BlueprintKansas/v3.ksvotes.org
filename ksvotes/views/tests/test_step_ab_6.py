# -*- coding: utf-8 -*-
from ksvotes.views.vr.example_form import signature_img_string
from ksvotes.models import Registrant
from test_plus import TestCase
import json


class AB6TestCase(TestCase):
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
                    "ab_identification": "nnnnn",
                    "elections": "General (11/7/2018)",
                }
            ),
            county="TEST",
            reg_lookup_complete=True,
            addr_lookup_complete=True,
            is_citizen=True,
            party="unaffiliated",
        )
        registrant.save()
        session = self.client.session
        session["id"] = str(registrant.session_id)
        session.save()
        return registrant

    def test_ab_6_no_signature_provided(self):
        self.create_registrant()
        form_payload = {}
        response = self.client.post("/ab/preview/", data=form_payload)
        self.assertEqual(response.status_code, 200)

    def test_ab_6_bad_signature_provided(self):
        self.create_registrant()
        form_payload = {"signature_string": "foobar"}
        response = self.client.post("/ab/preview/", data=form_payload)
        self.assertEqual(response.status_code, 200)

    def test_valid_ab_6_returns_redirect(self):
        self.create_registrant()
        form_payload = {"signature_string": signature_img_string}
        response = self.client.post("/ab/preview/", data=form_payload)
        self.assertRedirects(response, "/ab/affirmation/", status_code=302)

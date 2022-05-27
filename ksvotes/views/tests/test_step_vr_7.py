# -*- coding: utf-8 -*-
from ksvotes.views.vr.example_form import signature_img_string
from test_plus import TestCase
from ksvotes.models import Registrant
import json


class StepVR7TestCase(TestCase):
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
                    "signature_string": signature_img_string,  # dummy
                    "vr_form": signature_img_string,  # dummy
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

    def test_no_affirmation(self):
        registrant = self.create_registrant()
        form_payload = {}
        response = self.client.post("/vr/affirmation/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertFalse(registrant.try_value("affirmation"))

    def test_with_affirmation(self):
        registrant = self.create_registrant()
        form_payload = {"affirmation": "true"}
        response = self.client.post("/vr/affirmation/", data=form_payload)
        self.assertRedirects(response, "/vr/submission/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(
            registrant.try_value("vr_form_message_id"),
            "set SEND_EMAIL env var to enable email",
        )

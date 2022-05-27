# -*- coding: utf-8 -*-
from test_plus import TestCase
from ksvotes.models import Registrant
import json
from ksvotes.views.vr.example_form import signature_img_string


class StepAB7TestCase(TestCase):
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
                    "ab_forms": [signature_img_string],  # dummy
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
        response = self.client.post("/ab/affirmation/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertFalse(registrant.ab_completed_at)

    def test_with_affirmation(self):
        registrant = self.create_registrant()
        form_payload = {"affirmation": "true"}
        response = self.client.post("/ab/affirmation/", data=form_payload)
        self.assertRedirects(response, "/ab/submission/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(
            registrant.try_value("ab_forms_message_id"),
            "set SEND_EMAIL env var to enable email",
        )
        self.assertEqual(
            registrant.try_value("ab_id_action_email_sent"),
            "set SEND_EMAIL env var to enable email",
        )
        self.assertTrue(registrant.ab_completed_at)

    def test_with_affirmation_and_ab_id(self):
        registrant = self.create_registrant()
        registrant.update({"ab_identification": "xxxxx"})
        registrant.save()
        form_payload = {"affirmation": "true"}
        response = self.client.post("/ab/affirmation/", data=form_payload)
        registrant.refresh_from_db()
        self.assertRedirects(response, "/ab/submission/", status_code=302)
        self.assertEqual(
            registrant.try_value("ab_forms_message_id"),
            "set SEND_EMAIL env var to enable email",
        )
        self.assertFalse(registrant.try_value("ab_id_action_email_sent"))
        self.assertTrue(registrant.ab_completed_at)

    def test_with_permanent_election_no_ab_id(self):
        registrant = self.create_registrant()
        registrant.ab_permanent = True
        registrant.save()
        form_payload = {"affirmation": "true"}
        response = self.client.post("/ab/affirmation/", data=form_payload)
        registrant.refresh_from_db()
        self.assertRedirects(response, "/ab/submission/", status_code=302)
        self.assertEqual(
            registrant.try_value("ab_forms_message_id"),
            "set SEND_EMAIL env var to enable email",
        )
        self.assertFalse(registrant.try_value("ab_id_action_email_sent"))
        self.assertTrue(registrant.ab_completed_at)

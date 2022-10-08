# -*- coding: utf-8 -*-
from ksvotes.tests.test_utils import KSVotesTestCase
from ksvotes.models import Registrant
import json


class StepAB5TestCase(KSVotesTestCase):
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
                    "elections": "General",
                }
            ),
            county="TEST",
            reg_lookup_complete=True,
            addr_lookup_complete=True,
            is_citizen=True,
        )
        registrant.save()
        self.update_session(registrant)
        return registrant

    def test_ab_5_no_id_provided_ok(self):
        registrant = self.create_registrant()
        form_payload = {}
        response = self.client.post("/ab/identification/", data=form_payload)
        self.assertRedirects(response, "/ab/preview/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("ab_identification"), "")

    def test_invalid_ab_5_reloads_form(self):
        registrant = self.create_registrant()
        form_payload = {"ab_identification": "nnnnn"}
        response = self.client.post("/ab/identification/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("ab_identification"), "")

    def test_valid_ab_5_redirects_to_preview(self):
        registrant = self.create_registrant()
        form_payload = {"ab_identification": "K00000000"}
        response = self.client.post("/ab/identification/", data=form_payload)
        self.assertRedirects(response, "/ab/preview/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("ab_identification"), "K00-00-0000")

    def test_ab_permanent_skips_step_5(self):
        registrant = self.create_registrant()
        registrant.ab_permanent = True
        registrant.save()
        response = self.client.get("/ab/identification/")
        self.assertRedirects(response, "/en/ab/preview/", status_code=302)

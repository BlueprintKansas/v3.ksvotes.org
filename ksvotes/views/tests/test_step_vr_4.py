# -*- coding: utf-8 -*-
from test_plus import TestCase
from ksvotes.models import Registrant
import json


class StepVR4TestCase(TestCase):
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
                }
            ),
            county="TEST",
            reg_lookup_complete=True,
            addr_lookup_complete=True,
            is_citizen=True,
        )
        registrant.save()
        session = self.client.session
        session["id"] = str(registrant.session_id)
        session.save()
        return registrant

    def test_vr_4_no_party_provided(self):
        """
        An existing user tries to update their record, but does not provide a name field
        """
        registrant = self.create_registrant()
        form_payload = {}
        response = self.client.post("/vr/party/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertFalse(registrant.party)

    def test_valid_vr_4_returns_redirect(self):
        registrant = self.create_registrant()
        form_payload = {"party": "Unaffiliated"}
        response = self.client.post("/vr/party/", data=form_payload)
        self.assertRedirects(response, "/vr/identification/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.party, "Unaffiliated")

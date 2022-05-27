# -*- coding: utf-8 -*-
from test_plus import TestCase
from ksvotes.models import Registrant
import json


class StepVR2TestCase(TestCase):
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
            is_citizen=True,
        )
        registrant.save()
        session = self.client.session
        session["id"] = str(registrant.session_id)
        session.save()
        return registrant

    def test_vr_2_no_name_provided(self):
        """
        An existing user tries to update their record, but does not provide a name field
        """
        registrant = self.create_registrant()
        form_payload = {}
        response = self.client.post("/vr/name/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("name_first"), "foo")

    def test_valid_vr_2_returns_redirect(self):
        registrant = self.create_registrant()
        form_payload = {
            "prefix": "mr",
            "name_first": "foo",
            "name_last": "baz",
            "name_middle": "bar",
        }

        response = self.client.post("/vr/name/", data=form_payload)
        self.assertRedirects(response, "/vr/address/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("prefix"), "mr")
        self.assertEqual(registrant.try_value("name_last"), "baz")

    def test_valid_vr_2_prev_name_missing_fields(self):
        registrant = self.create_registrant()
        form_payload = {
            "prefix": "mr",
            "name_first": "foo",
            "name_last": "baz",
            "name_middle": "bar",
            "has_prev_name": "true",
        }

        response = self.client.post("/vr/name/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("name_last"), "bar")  # nothing changed

    def test_vr_2_prev_name(self):
        registrant = self.create_registrant()
        form_payload = {
            "prefix": "mr",
            "name_first": "foo",
            "name_last": "baz",
            "name_middle": "bar",
            "has_prev_name": "true",
            "prev_name_first": "Jane",
            "prev_name_last": "Smith",
        }

        response = self.client.post("/vr/name/", data=form_payload)
        self.assertRedirects(response, "/vr/address/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("prefix"), "mr")
        self.assertEqual(registrant.try_value("name_last"), "baz")
        self.assertEqual(registrant.try_value("prev_name_last"), "Smith")

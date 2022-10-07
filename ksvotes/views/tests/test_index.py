# -*- coding: utf-8 -*-
from ksvotes.tests.test_utils import KSVotesTestCase
from ksvotes.models import Registrant
import json
from django.test.utils import override_settings


class Step0TestCase(KSVotesTestCase):
    def find_current_registrant(self):
        return Registrant.find_by_session(self.client.session.get("id"))

    def test_create_new_session_step_0(self):
        """
        A new user has a session id created for them and stored
        """
        form_payload = {
            "name_first": "foo",
            "name_last": "bar",
            "dob": "01/01/2000",
            "email": "foo@example.com",
            "zip": "12345",
        }
        self.assertFalse(self.client.session.get("id"))
        response = self.client.post("/", data=form_payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get("id"))
        registrant = self.find_current_registrant()
        self.assertTrue(registrant.reg_lookup_complete)

    def test_update_name_step_0_session_exists_already(self):
        """
        A returning user with a session id updates the existing registrant model.
        """
        # if active session exists update step 0 records
        registrant_data = {
            "name_first": "foo",
            "name_last": "bar",
            "dob": "01-01-2018",
            "email": "foo@bar.com",
            "phone": "555-555-5555",
        }
        # registration value should be automatically encrypted and decrypted
        new_registrant = Registrant(
            lang="en",
            county="Johnson",
            registration=json.dumps(registrant_data),
        )
        new_registrant.save()

        self.update_session(new_registrant)

        current_registrant = self.find_current_registrant()

        self.assertEqual(current_registrant.try_value("name_first"), "foo")

        name_update = {
            "name_first": "baz",
            "zip": "12345",
        }
        current_registrant.update(name_update)
        current_registrant.save()

        current_registrant_updated = self.find_current_registrant()
        self.assertEqual(current_registrant_updated.try_value("name_first"), "baz")
        self.assertEqual(current_registrant_updated.try_value("zip"), "12345")
        self.assertEqual(current_registrant_updated.id, current_registrant.id)

    def test_registered_voter_input_returns_redirect_change_or_apply(self):
        """
        An already registered voter returns a redirect to change-or-apply endpoint
        """
        form_payload = {
            "name_first": "Kris",
            "name_last": "Kobach",
            "dob": "03/26/1966",
            "email": "foo@example.com",
            "zip": "66044",
        }
        self.assertFalse(self.client.session.get("id"))

        response = self.client.post("/", data=form_payload)
        self.assertRedirects(response, "/change-or-apply/", status_code=302)

    @override_settings(ENABLE_AB=False)
    def test_skip_sos_check_vr_only_returns_redirect_step_1(self):
        form_payload = {
            "name_first": "foo",
            "name_last": "bar",
            "dob": "02/02/1999",
            "email": "foo@example.com",
            "zip": "12345",
            "skip-sos": "true",
        }
        response = self.client.post("/", data=form_payload)
        self.assertRedirects(response, "/vr/citizenship/")

    def test_unregistered_voter_input_returns_redirect_step_1(self):
        form_payload = {
            "name_first": "foo",
            "name_last": "bar",
            "dob": "02/02/1999",
            "email": "foo@example.com",
            "zip": "12345",
        }
        response = self.client.post("/", data=form_payload)
        self.assertRedirects(response, "/change-or-apply/", status_code=302)

    def test_dob_all_digits(self):
        form_payload = {
            "name_first": "foo",
            "name_last": "bar",
            "dob": "07071999",
            "email": "foo@example.com",
            "zip": "12345",
        }
        response = self.client.post("/", data=form_payload)
        self.assertRedirects(response, "/change-or-apply/", status_code=302)

    def test_dob_invalid_digits(self):
        form_payload = {
            "name_first": "foo",
            "name_last": "bar",
            "dob": "0707199",
            "email": "foo@example.com",
            "zip": "12345",
        }
        response = self.client.post("/", data=form_payload)
        self.assertEqual(response.status_code, 200)

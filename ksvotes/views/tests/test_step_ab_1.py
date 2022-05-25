# -*- coding: utf-8 -*-
from test_plus import TestCase
from ksvotes.models import Registrant
import json
from ksvotes.utils import is_even_year
from django.utils import timezone


class StepAB1TestCase(TestCase):
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
        session = self.client.session
        session["id"] = str(registrant.session_id)
        session.save()
        return registrant

    def test_ab_1_general_election(self):
        self.create_registrant()
        form_payload = {"elections": "General"}
        response = self.client.post("/ab/election_picker/", data=form_payload)
        self.assertRedirects(response, "/ab/address/", status_code=302)

    def test_ab_1_general_election_already_registered(self):
        registrant = self.create_registrant()
        registrant.vr_completed_at = timezone.now()
        registrant.save()
        form_payload = {"elections": "General"}
        response = self.client.post("/ab/election_picker/", data=form_payload)
        self.assertRedirects(response, "/ab/identification/", status_code=302)

    def test_ab_1_general_and_primary_no_party(self):
        self.create_registrant()
        form_payload = {"elections": ["General", "Primary"]}
        response = self.client.post("/ab/election_picker/", data=form_payload)
        if is_even_year():
            assert response.status_code == 200
        else:
            self.assertRedirect(response, "/ab/address/", status_code=302)

    def test_ab_1_general_and_primary_with_party(self):
        registrant = self.create_registrant()
        form_payload = {"elections": ["General", "Primary"], "party": "Republican"}
        response = self.client.post("/ab/election_picker/", data=form_payload)
        self.assertRedirects(response, "/ab/address/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.party, "Republican")
        self.assertEqual(registrant.try_value("elections"), "General|Primary")

    def test_ab_1_permanent_no_party(self):
        self.create_registrant()
        form_payload = {
            "elections": ["permanent"],
            "perm_reason": "some reason",
        }
        response = self.client.post("/ab/election_picker/", data=form_payload)
        self.assertRedirects(response, "/ab/address/", status_code=302)

    def test_ab_1_permanent_no_reason(self):
        self.create_registrant()
        form_payload = {
            "elections": ["permanent"],
            "party": "Republican",
        }
        response = self.client.post("/ab/election_picker/", data=form_payload)
        assert response.status_code == 200

    def test_ab_1_permanent_with_party_and_reason(self):
        self.create_registrant()
        form_payload = {
            "elections": ["permanent"],
            "party": "Republican",
            "perm_reason": "some reason",
        }
        response = self.client.post("/ab/election_picker/", data=form_payload)
        self.assertRedirects(response, "/ab/address/", status_code=302)

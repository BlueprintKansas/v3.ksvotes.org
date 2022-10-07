# -*- coding: utf-8 -*-
from ksvotes.tests.test_utils import KSVotesTestCase
from ksvotes.models import Registrant
import json


class StepAB3TestCase(KSVotesTestCase):
    def create_registrant(self):
        registrant = Registrant(
            registration=json.dumps(
                {
                    "name_first": "foo",
                    "name_last": "bar",
                    "dob": "01/01/2000",
                    "email": "foo@example.com",
                    "elections": "General",
                }
            ),
            county="TEST",
            reg_lookup_complete=True,
            is_citizen=True,
        )
        registrant.save()
        self.update_session(registrant)
        return registrant

    def test_ab_3_no_address_provided(self):
        registrant = self.create_registrant()
        form_payload = {}
        response = self.client.post("/ab/address/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "")

    def test_ab_3_single_valid_address(self):
        registrant = self.create_registrant()
        form_payload = {
            "addr": "707 Vermont St",
            "unit": "Room A",
            "city": "Lawrence",
            "state": "KANSAS",
            "zip": "66044",
        }
        response = self.client.post("/ab/address/", data=form_payload)
        self.assertRedirects(response, "/ab/identification/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "707 Vermont St")

        self.assertTrue(registrant.try_value("validated_addresses"))
        self.assertEqual(
            registrant.try_value("validated_addresses")["current_address"]["state"],
            "KS",
        )

    def test_ab_3_single_address_no_county(self):
        registrant = self.create_registrant()
        registrant.county = None
        registrant.save()
        form_payload = {
            "addr": "707 Vermont St",
            "unit": "Room A",
            "city": "Lawrence",
            "state": "KANSAS",
            "zip": "66044",
        }
        response = self.client.post("/ab/address/", data=form_payload)
        self.assertRedirects(response, "/ab/identification/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.county, "Douglas")

    def test_ab_3_single_invalid_address(self):
        registrant = self.create_registrant()
        form_payload = {
            "addr": "123 Fake St",
            "city": "FakeTown",
            "state": "NA",
            "zip": "00000",
        }

        response = self.client.post("/ab/address/", data=form_payload)
        self.assertRedirects(response, "/ab/identification/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "123 Fake St")
        self.assertFalse(registrant.try_value("validated_addresses"))

    def test_ab_3_with_mail_address(self):
        registrant = self.create_registrant()
        form_payload = {
            "addr": "707 Vermont St",
            "unit": "Room A",
            "city": "Lawrence",
            "state": "KANSAS",
            "zip": "66044",
            "has_mail_addr": True,
            "mail_addr": "707 Vermont St",
            "mail_unit": "Room B",
            "mail_city": "Lawrence",
            "mail_state": "KANSAS",
            "mail_zip": "66044",
        }

        response = self.client.post("/ab/address/", data=form_payload)
        self.assertRedirects(response, "/ab/identification/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "707 Vermont St")
        self.assertEqual(
            registrant.try_value("validated_addresses")["current_address"]["state"],
            "KS",
        )
        self.assertEqual(
            registrant.try_value("validated_addresses")["mail_addr"]["unit"], "RM B"
        )

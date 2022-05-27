# -*- coding: utf-8 -*-
from test_plus import TestCase
from ksvotes.models import Registrant
import json


class StepVR3TestCase(TestCase):
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

    def test_vr_3_no_address_provided(self):
        """
        An existing user tries to post without an address provided
        """

        registrant = self.create_registrant()
        form_payload = {}
        response = self.client.post("/vr/address/", data=form_payload)
        self.assertEqual(response.status_code, 200)
        registrant.refresh_from_db()
        self.assertFalse(registrant.try_value("addr"))

    def test_vr_3_single_valid_address(self):
        """
        An existing user provides a valid address, but no previous address or mailing address.
        """

        registrant = self.create_registrant()
        form_payload = {
            "addr": "707 Vermont St",
            "unit": "Room A",
            "city": "Lawrence",
            "state": "KANSAS",
            "zip": "66044",
        }

        response = self.client.post("/vr/address/", data=form_payload)
        self.assertRedirects(response, "/vr/party/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "707 Vermont St")
        self.assertTrue(registrant.try_value("validated_addresses"))
        self.assertEqual(
            registrant.try_value("validated_addresses")["current_address"]["state"],
            "KS",
        )

    def test_vr_3_single_address_no_county(self):
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

        response = self.client.post("/vr/address/", data=form_payload)
        self.assertRedirects(response, "/vr/party/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.county, "Douglas")

    def test_vr_3_single_address_wrong_zip(self):
        registrant = self.create_registrant()
        form_payload = {
            "addr": "707 Vermont St",
            "unit": "Room A",
            "city": "Lawrence",
            "state": "KANSAS",
            "zip": "66043",
        }

        response = self.client.post("/vr/address/", data=form_payload)
        self.assertRedirects(response, "/vr/party/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.county, "Douglas")

    def test_vr_3_single_invalid_address(self):
        """
        An existing user provides an invalid address, but no previous address or mailing address. Should still redirect.
        """

        registrant = self.create_registrant()
        form_payload = {
            "addr": "123 Fake St",
            "city": "FakeTown",
            "state": "NA",
            "zip": "00000",
        }

        response = self.client.post("/vr/address/", data=form_payload)
        self.assertRedirects(response, "/vr/party/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "123 Fake St")
        self.assertFalse(registrant.try_value("validated_addresses"))

    def test_vr_3_with_prev_address(self):
        """
        An existing user provides a valid address and valid prev address
        """
        registrant = self.create_registrant()
        form_payload = {
            "addr": "707 Vermont St",
            "unit": "Room A",
            "city": "Lawrence",
            "state": "KANSAS",
            "zip": "66044",
            "has_prev_addr": True,
            "prev_addr": "707 Vermont St",
            "prev_unit": "Room B",
            "prev_city": "Lawrence",
            "prev_state": "KANSAS",
            "prev_zip": "66044",
        }

        response = self.client.post("/vr/address/", data=form_payload)
        self.assertRedirects(response, "/vr/party/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "707 Vermont St")
        self.assertTrue(registrant.try_value("validated_addresses"))
        self.assertEqual(
            registrant.try_value("validated_addresses")["current_address"]["state"],
            "KS",
        )
        self.assertEqual(
            registrant.try_value("validated_addresses")["prev_addr"]["unit"], "RM B"
        )

    def test_vr_3_with_invalid_prev_address(self):
        """
        An existing user provides a valid address and invalid prev address
        """
        registrant = self.create_registrant()
        form_payload = {
            "addr": "707 Vermont St",
            "unit": "Room A",
            "city": "Lawrence",
            "state": "KANSAS",
            "zip": "66044",
            "has_prev_addr": True,
            "prev_addr": "123 Fake St",
            "prev_city": "FakeTown",
            "prev_state": "NA",
            "prev_zip": "00000",
        }

        response = self.client.post("/vr/address/", data=form_payload)
        self.assertRedirects(response, "/vr/party/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "707 Vermont St")
        self.assertTrue(registrant.try_value("validated_addresses"))
        self.assertEqual(
            registrant.try_value("validated_addresses")["current_address"]["state"],
            "KS",
        )
        self.assertTrue(
            registrant.try_value("validated_addresses")["prev_addr"]["error"]
        )

    def test_vr_3_with_mail_address(self):
        """
        An existing user provides a valid address and valid mailing address
        """
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

        response = self.client.post("/vr/address/", data=form_payload)
        self.assertRedirects(response, "/vr/party/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "707 Vermont St")
        self.assertTrue(registrant.try_value("validated_addresses"))
        self.assertEqual(
            registrant.try_value("validated_addresses")["current_address"]["state"],
            "KS",
        )
        self.assertEqual(
            registrant.try_value("validated_addresses")["mail_addr"]["unit"], "RM B"
        )

    def test_vr_3_with_invalid_mailing_address(self):
        registrant = self.create_registrant()
        form_payload = {
            "addr": "707 Vermont St",
            "unit": "Room A",
            "city": "Lawrence",
            "state": "KANSAS",
            "zip": "66044",
            "has_mail_addr": True,
            "mail_addr": "123 Fake St",
            "mail_city": "Faketown",
            "mail_state": "NA",
            "mail_zip": "00000",
        }

        response = self.client.post("/vr/address/", data=form_payload)
        self.assertRedirects(response, "/vr/party/", status_code=302)
        registrant.refresh_from_db()
        self.assertEqual(registrant.try_value("addr"), "707 Vermont St")
        self.assertTrue(registrant.try_value("validated_addresses"))
        self.assertEqual(
            registrant.try_value("validated_addresses")["current_address"]["state"],
            "KS",
        )
        self.assertTrue(
            registrant.try_value("validated_addresses")["mail_addr"]["error"]
        )

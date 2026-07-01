# -*- coding: utf-8 -*-
from unittest import TestCase, mock
from ksvotes.services.usps_api import USPS_API

# import logging

# logging.basicConfig(level=logging.DEBUG)

RESP = {
    "result": {
        "address": {
            "addressComponents": [
                {
                    "componentName": {"text": "707"},
                    "componentType": "street_number",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {
                        "languageCode": "en",
                        "text": "Vermont " "Street",
                    },
                    "componentType": "route",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"languageCode": "en", "text": "room " "a"},
                    "componentType": "subpremise",
                    "confirmationLevel": "UNCONFIRMED_BUT_PLAUSIBLE",
                },
                {
                    "componentName": {"languageCode": "en", "text": "Lawrence"},
                    "componentType": "locality",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"languageCode": "en", "text": "KS"},
                    "componentType": "administrative_area_level_1",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "66044"},
                    "componentType": "postal_code",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"languageCode": "en", "text": "USA"},
                    "componentType": "country",
                    "confirmationLevel": "CONFIRMED",
                },
                {
                    "componentName": {"text": "2371"},
                    "componentType": "postal_code_suffix",
                    "confirmationLevel": "CONFIRMED",
                    "inferred": True,
                },
            ],
            "formattedAddress": "707 Vermont Street room a, "
            "Lawrence, KS 66044-2371, USA",
            "postalAddress": {
                "addressLines": ["707 Vermont St " "room a"],
                "administrativeArea": "KS",
                "languageCode": "en",
                "locality": "Lawrence",
                "postalCode": "66044-2371",
                "regionCode": "US",
            },
            "unconfirmedComponentTypes": ["subpremise"],
        },
    }
}

FORM_PAYLOAD = {
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


@mock.patch("ksvotes.services.usps_api.API_KEY", "abc-123")
class USPSApiTestCase(TestCase):
    @mock.patch("ksvotes.services.usps_api.googlemaps.Client")
    def test_multiline_address(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.addressvalidation.return_value = RESP

        usps = USPS_API(FORM_PAYLOAD)
        addr = usps.validate_addresses()
        expected = {
            "current_address": {
                "address": "707 Vermont Street",
                "city": "Lawrence",
                "error": None,
                "state": "KS",
                "unit": "room a",
                "zip4": "2371",
                "zip5": "66044",
            },
            "prev_addr": {
                "address": "707 Vermont Street",
                "city": "Lawrence",
                "error": None,
                "state": "KS",
                "unit": "room a",
                "zip4": "2371",
                "zip5": "66044",
            },
        }
        self.assertEqual(expected, addr, "addresses parsed")

# -*- coding: utf-8 -*-
import os
import requests
import logging
import http.client
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

DUMMY = "dummy"
PROD_URL = "https://apis.usps.com"
TEST_URL = "TODO"
SKIPPED = "Address verification skipped."


class Client:
    def __init__(self, token_type, token):
        self.authz_header = f"{token_type} {token}"

    def city_state(self, zip_code: str) -> dict[str, str]:
        params = {
            "ZIPCode": zip_code,
        }
        url = f"{PROD_URL}/addresses/v3/city-state?{urlencode(params)}"
        headers = {
            "Authorization": self.authz_header,
            "Content-Type": "application/json",
        }
        resp = requests.get(url, headers=headers)
        return resp.json()

    def standardize(self, address: dict[str, str]):
        params = {
            "streetAddress": address["address"],
            "secondaryAddress": address["address_extended"],
            "city": address["city"],
            "state": address["state"],
            "ZIPCode": address["zip_code"],
        }

        # USPS requires 2-letter state abbreviations
        if params["state"] == "KANSAS":
            params["state"] = "KS"
        if len(params["state"]) != 2:
            city_state = self.city_state(params["ZIPCode"])
            params["state"] = city_state.get("state")

        url = f"{PROD_URL}/addresses/v3/address?{urlencode(params)}"
        headers = {
            "Authorization": self.authz_header,
            "Content-Type": "application/json",
        }
        resp = requests.get(url, headers=headers).json()

        # if we exceed quota rate, just return
        if resp.get("error") and resp.get("error").get("code") == "429":
            return address | {"skipped": True}

        # TODO parse nuances in corrections, etc.
        r = resp.get("address")
        if r is None:
            raise ValueError(resp.json())

        standard = {
            "address": r.get("streetAddress"),
            "address_extended": r.get("secondaryAddress"),
            "city": r.get("city"),
            "state": r.get("state"),
            "zip_code": "-".join([r.get("ZIPCode"), r.get("ZIPPlus4")]),
        }
        return standard


class USPS_API:
    def __init__(self, address_payload=None):
        self.address_payload = address_payload
        self.usps_key = os.getenv("USPS_KEY")
        self.usps_secret = os.getenv("USPS_SECRET")
        self.address_order = ["current_address"]

        if self.usps_key != DUMMY:
            self._init_client()
        else:
            self._init_dummy_client()

    def _init_client(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.usps_key,
            "client_secret": self.usps_secret,
        }
        url = f"{PROD_URL}/oauth2/v3/token"
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        http.client.HTTPConnection.debuglevel = 1

        response = requests.post(url, json=payload)
        resp_payload = response.json()
        self.client = Client(resp_payload["token_type"], resp_payload["access_token"])

    def _init_dummy_client(self):
        self.client = None

    def marshall_single_address(self, address):
        """
        Convert a single address from USPS into a dictionary with the correct k,vs or an en error
        """
        marshalled_address = {"error": None}
        if isinstance(address, dict):
            for k, v in address.items():
                if k == "address_extended":
                    marshalled_address["unit"] = v
                elif k == "skipped":
                    marshalled_address["error"] = SKIPPED
                else:
                    marshalled_address[k] = v
        elif isinstance(address, ValueError):
            marshalled_address["error"] = "There was an issue validating your address."

        return marshalled_address

    def marshall_address_results(self, validated_addresses):
        """
        Take a USPS result and determine if it is a single address or list of addresses, then marshal each address and return the full marshalled dictionary.
        """
        marshalled_addresses = {}
        if isinstance(validated_addresses, dict):
            marshalled_addresses["current_address"] = self.marshall_single_address(
                validated_addresses
            )
        elif isinstance(validated_addresses, list):
            for count, address in enumerate(validated_addresses):
                marshalled_addresses[self.address_order[count]] = (
                    self.marshall_single_address(address)
                )
        else:
            raise "Invalid addresses, cannot marshall"

        # import code; code.interact(local=dict(globals(), **locals()))

        return marshalled_addresses

    def validate_addresses(self):
        """
        Return values of usps lookup.  Keep track of order of addresses if multiple provided.
        """
        addresses = []

        # always expect the current address
        addresses.append(
            dict(
                [
                    ("address", self.address_payload.get("addr", "")),
                    ("city", self.address_payload.get("city", "")),
                    ("state", self.address_payload.get("state", "")),
                    ("zip_code", self.address_payload.get("zip", "")),
                    ("address_extended", self.address_payload.get("unit", "")),
                ],
                error=None,
            )
        )

        # construct additional addresses for request and update address_order
        if self.address_payload.get("has_prev_addr", None) == True:
            self.address_order.append("prev_addr")
            addresses.append(
                dict(
                    [
                        ("address", self.address_payload.get("prev_addr", "")),
                        ("city", self.address_payload.get("prev_city", "")),
                        ("state", self.address_payload.get("prev_state", "")),
                        ("zip_code", self.address_payload.get("prev_zip", "")),
                        ("address_extended", self.address_payload.get("prev_unit", "")),
                    ],
                    error=None,
                )
            )

        if self.address_payload.get("has_mail_addr", None) == True:
            self.address_order.append("mail_addr")
            addresses.append(
                dict(
                    [
                        ("address", self.address_payload.get("mail_addr", "")),
                        ("city", self.address_payload.get("mail_city", "")),
                        ("state", self.address_payload.get("mail_state", "")),
                        ("zip_code", self.address_payload.get("mail_zip", "")),
                        ("address_extended", self.address_payload.get("mail_unit", "")),
                    ],
                    error=None,
                )
            )

        logger.debug("Trying USPS address lookup")
        results = self.verify_with_usps(addresses)
        logger.debug("USPS API returned {}".format(results))
        if results:
            return self.marshall_address_results(results)
        else:
            return False

    def verify_with_usps(self, addresses):
        responses = []
        for address in addresses:
            r = self.client.standardize(address)
            responses.append(r)
        return responses
        try:
            responses = []
            for address in addresses:
                r = self.client.standardize(address)
                logger.warning(r)
                responses.append(r)
            return responses
        except Exception:
            return False

# -*- coding: utf-8 -*-
"""
The USPS module used to wrap the USPS API but now wraps the Google Maps API.
The interface and class names remain the same but internals changed.
"""

import os
import logging
import googlemaps
import pprint

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DUMMY = "dummy"
SKIPPED = "Address verification skipped."
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


class USPSError(Exception):
    pass


class DummyClient:
    """Use for CI tests when we don't want to ping USPS"""

    def standardize(self, address: dict[str, str]) -> dict[str, str]:
        address["zip5"] = address.pop("zip_code")
        unit = address.get("address_extended", "") or ""
        if unit and unit.startswith("Room"):
            address["address_extended"] = address["address_extended"].replace(
                "Room", "RM"
            )

        for k, v in address.items():
            if v is None:
                continue
            address[k] = v.upper()

        if address["state"] == "KANSAS":
            address["state"] = "KS"

        if address["zip5"] == "66043" and address["city"] == "LAWRENCE":
            address["zip5"] = "66044"
            address["zip4"] = "2371"

        if address["zip5"] == "66044" and address["address"] == "707 VERMONT ST":
            address["zip4"] = "2371"

        if address["state"] == "NA":
            raise ValueError("invalid state code")

        if not address["zip5"] or address["zip5"] == "00000":
            raise ValueError("invalid ZIP")

        if address["city"] in ["SPECIFIC CITY", "SOME PLACE", "NOWHERE"]:
            raise ValueError("invalid city")

        return address


class Client:
    def city_state(self, zip_code: str) -> dict[str, str]:
        gmaps = googlemaps.Client(key=API_KEY)
        resp = gmaps.geocode(zip_code)

        logger.debug(pprint.pformat(resp))

        # Extract address components from the first result
        address_components = resp[0]["address_components"]

        city = None
        state = None

        # Loop through components to extract city and state
        for component in address_components:
            types = component.get("types", [])

            # 'locality' usually represents the city
            if "locality" in types:
                city = component["long_name"]
            # In case 'locality' is missing, fallback
            elif "sublocality_level_1" in types and not city:
                city = component["long_name"]
            elif "administrative_area_level_3" in types and not city:
                city = component["long_name"]

            # 'administrative_area_level_1' represents the state
            if "administrative_area_level_1" in types:
                state = component["short_name"]

        return {"city": city, "state": state}

    def standardize(self, address: dict[str, str]):
        zips = address.get("zip_code").split("-")
        if len(zips) == 2:
            zip5 = zips[0]
        else:
            zip5 = zips[0]

        # USPS requires 2-letter state abbreviations
        state = address.get("state")
        if state == "KANSAS":
            state = "KS"
        if state and len(state) != 2:
            city_state = self.city_state(zip5)
            state = city_state.get("state")
        state = state.upper() if state else None

        gmaps = googlemaps.Client(key=API_KEY)
        # let google parse the address so we can include state and zip
        addr = ", ".join(
            filter(
                lambda p: p,
                [
                    address["address"],
                    address.get("address_extended"),
                    address["city"],
                    f"{state if state else ''} {zip5}",
                ],
            )
        )
        resp = gmaps.addressvalidation(
            addressLines=[addr], regionCode="US", enableUspsCass=True
        )

        logger.debug(pprint.pformat(resp))

        r = resp.get("result", dict()).get("address")
        if r is None:
            raise ValueError(resp)

        norm = {}
        for comp in r["addressComponents"]:
            level = comp["confirmationLevel"]
            logger.debug(f"{level=} {comp=}")
            if level not in ["CONFIRMED", "UNCONFIRMED_BUT_PLAUSIBLE"]:
                continue
            norm[comp["componentType"]] = comp["componentName"]["text"]

        logger.debug(f"{r=} {norm=}")

        standard = {
            "address": f"{norm['street_number']} {norm['route']}",
            "address_extended": norm.get(
                "subpremise", norm.get("floor", norm.get("room"))
            ),
            "city": norm.get("locality"),
            "state": norm.get("administrative_area_level_1"),
            "zip5": norm.get("postal_code"),
            "zip4": norm.get("postal_code_suffix"),
        }
        return standard


class USPS_API:
    def __init__(self, address_payload=None):
        self.address_payload = address_payload
        self.address_order = ["current_address"]

        if API_KEY != DUMMY:
            self._init_client()
        else:
            self._init_dummy_client()

    def _init_client(self):
        self.client = Client()

    def _init_dummy_client(self):
        self.client = DummyClient()

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
            try:
                r = self.client.standardize(address)
                responses.append(r)
            except Exception as err:
                responses.append(err)

        logger.debug(f"{responses=}")

        if len(responses) == 1 and isinstance(responses[0], ValueError):
            return False
        return responses

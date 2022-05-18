# -*- coding: utf-8 -*-
from test_plus import TestCase
import json
from ksvotes.models import Registrant, Clerk
from datetime import datetime
import os
from unittest import mock


class RegistrantTestCase(TestCase):
    def test_registration(self):
        # data should be dictionary
        registrant_data = json.dumps(
            {
                "name_first": "foo",
                "name_last": "bar",
                "dob": "01-01-2018",
                "email": "foo@bar.com",
                "phone": "555-555-5555",
            }
        )
        # registration value should be automatically encrypted and decrypted
        registrant = Registrant.objects.create(
            lang="en",
            county="Johnson",
            registration=registrant_data,
        )

        # confirm that registration was modified from dictionary value
        assert isinstance(registrant.registration, (dict)) is False

        # confirm that registration_value is returned decrypted and marshalled to dictionary
        assert isinstance(registrant.registration_as_dict(), (dict))
        assert registrant.try_value("name_first") == "foo"

        # query by uuid
        registrant_uuid = Registrant.objects.get(session_id=registrant.session_id)
        assert registrant_uuid.try_value("name_first") == "foo"

        # defaults to empty dict
        assert Registrant().registration_as_dict() == {}

        # to_dict
        assert registrant.to_dict()["registration"]["name_first"] == "foo"

    def test_prepopulate_address(self):
        sosrec = {
            "Address": "123 Main St #456 Wichita, KS, 12345",
            "Party": "Republican",
        }
        r = Registrant()
        r.populate_address(sosrec)

        assert r.try_value("addr") == "123 Main St"
        assert r.try_value("unit") == "# 456"
        assert r.try_value("city") == "Wichita"
        assert r.try_value("state") == "KS"
        assert r.try_value("zip") == "12345"

        assert r.precinct_address() == "123 Main St Wichita KS 12345"

    def test_prepopulate_secure_voter(self):
        sosrec = {"Address": "No information available", "Party": "Republican"}
        r = Registrant()
        r.populate_address(sosrec)

        assert r.try_value("addr") == ""
        assert r.try_value("unit") == ""
        assert r.try_value("city") == ""
        assert r.try_value("state") == "KANSAS"
        assert r.try_value("zip") == ""

    def test_signed_at_timezone(self):
        r = Registrant()
        r.signed_at = datetime(2018, 10, 18, 3, 0)

        assert r.signed_at_central_tz().strftime("%m/%d/%Y") == "10/17/2018"

    def test_redaction(self):
        r = Registrant(registration=json.dumps({"foo": "bar"}))
        r.update(
            {
                "ab_identification": "abc123",
                "identification": "def456",
                "signature_string": "i am me",
                "ref": "test",
            }
        )
        r.save()

        assert r.try_value("ab_identification") == "abc123"
        assert r.try_value("identification") == "def456"
        assert r.try_value("signature_string") == "i am me"
        assert r.try_value("foo") == "bar"
        assert r.ab_identification_found is None
        assert r.identification_found is None
        assert r.redacted_at is None
        assert r.ref == "test"

        Registrant.redact_pii(datetime.utcnow())

        reg = Registrant.find_by_session(r.session_id)

        assert reg.ab_identification_found
        assert reg.identification_found
        assert reg.redacted_at is not None
        assert reg.try_value("ab_identification") == "[REDACTED]"
        assert reg.try_value("identification") == "[REDACTED]"
        assert reg.try_value("signature_string") == "[REDACTED]"
        assert reg.try_value("foo") == "bar"
        assert reg.ref == "test"

    def test_set_value(self):
        r = Registrant()
        r.set_value("ref", "test")
        assert r.ref == "test"

    def test_has_value_for_req(self):
        r = Registrant(registration=json.dumps({"foo": "bar"}))
        r.ref = "test"
        assert r.has_value_for_req("foo") is True
        assert r.has_value_for_req("bar") is False
        assert r.has_value_for_req("redacted_at") is False
        assert r.has_value_for_req("ref") is True

    def test_try_clerk(self):
        Clerk.objects.create(
            county="foo",
            officer="bar",
            email="foo@bar.com",
            phone="5555555555",
            fax="5555555555",
            address1="123 fake st",
            address2="ste 107",
            city="springfield",
            state="KANSAS",
            zip="55555",
        )
        r = Registrant.objects.create(county="foo")
        assert r.try_clerk().county == "foo"

        r_no_clerk = Registrant.objects.create(county="bar")
        assert r_no_clerk.try_clerk() is None

    @mock.patch.dict(os.environ, {"DEMO_UUID": "e39966ee8a23441fb4adc257233b617f"})
    def test_demo(self):
        Registrant.load_fixtures()
        r = Registrant.objects.first()
        assert r.is_demo() is True

    def test_get_dob_year(self):
        r = Registrant(registration=json.dumps({"dob": "01/01/2000"}))
        assert r.get_dob_year() == 2000

    def test_best_zip5(self):
        r = Registrant(
            registration=json.dumps(
                {
                    "zip": "99999",
                    "validated_addresses": {"current_address": {"zip5": "12345"}},
                }
            )
        )
        assert r.best_zip5() == "12345"

        r = Registrant(registration=json.dumps({"zip": "99999"}))
        assert r.best_zip5() == "99999"

    def test_middle_initial(self):
        r = Registrant(registration=json.dumps({"name_middle": "Eugene"}))
        assert r.middle_initial() == "E"
        r = Registrant()
        assert r.middle_initial() is None

    def test_updated_since(self):
        r = Registrant()
        r.save()
        assert r.updated_since(1) is True

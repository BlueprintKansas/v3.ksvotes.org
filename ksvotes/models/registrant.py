# -*- coding: utf-8 -*-
from .base import TimeStampedModel
from django.db import models
from django.core.paginator import Paginator
import uuid
import usaddress
import pytz
import os
from datetime import datetime, timedelta
import json
from django.utils import timezone
from fernet_fields import EncryptedTextField


class Registrant(TimeStampedModel):
    class Meta:
        indexes = [
            models.Index(fields=["vr_completed_at"]),
            models.Index(fields=["ab_completed_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]

    # PII all encrypted in a "registration" column
    registration = EncryptedTextField()

    redacted_at = models.DateTimeField(default=None, null=True)
    vr_completed_at = models.DateTimeField(default=None, null=True)
    ab_completed_at = models.DateTimeField(default=None, null=True)
    ab_permanent = models.BooleanField(default=None, null=True)
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, null=False)
    ref = models.CharField(max_length=255, null=True)
    is_citizen = models.BooleanField(default=None, null=True)
    is_eighteen = models.BooleanField(default=None, null=True)
    dob_year = models.IntegerField(null=True)
    party = models.CharField(max_length=255, null=True)
    county = models.CharField(max_length=255, null=True)
    lang = models.CharField(max_length=2, null=True)
    signed_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    reg_lookup_complete = models.BooleanField(default=False, null=True)
    addr_lookup_complete = models.BooleanField(default=False, null=True)
    reg_found = models.BooleanField(default=None, null=True)
    identification_found = models.BooleanField(default=None, null=True)
    ab_identification_found = models.BooleanField(default=None, null=True)

    @classmethod
    def lookup_by_session_id(cls, sid):
        return cls.objects.get(session_id=sid)

    @classmethod
    def find_by_session(cls, sid):
        return cls.lookup_by_session_id(sid)

    def is_demo(self):
        return self.session_id == uuid.UUID(os.getenv("DEMO_UUID"))

    @classmethod
    def load_fixtures(cls):
        if not os.getenv("DEMO_UUID"):  # pragma: no cover
            raise Exception("Must define env var DEMO_UUID")

        r, _ = cls.objects.get_or_create(session_id=os.getenv("DEMO_UUID"))
        r.registration = {}
        r.update(
            {
                "name_first": "No",
                "name_middle": "Such",
                "name_last": "Person",
                "dob": "01/01/2000",
                "addr": "123 Main St",
                "city": "Nowhere",
                "state": "KS",
                "zip": "12345",
                "email": "nosuchperson@example.com",
                "phone": "555-555-1234",
                "identification": "NONE",
            }
        )
        r.party = "Unaffiliated"
        r.reg_lookup_complete = True
        r.addr_lookup_complete = True
        r.is_citizen = True
        r.county = "TEST"
        r.save()

    @classmethod
    def for_each(cls, func, *where):  # pragma: no cover
        queryset = cls.objects.filter(*where).all()
        paginator = Paginator(queryset, 200)
        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            for r in page.object_list:
                func(r)

    @classmethod
    def redact(cls, reg):
        fields = [
            "identification",
            "ab_identification",
            "vr_form",
            "ab_forms",
            "signature_string",
        ]
        if reg.try_value("identification"):
            reg.identification_found = True
        if reg.try_value("ab_identification"):
            reg.ab_identification_found = True
        for f in fields:
            reg.set_value(f, "[REDACTED]")
        reg.redacted_at = timezone.now()

    @classmethod
    def redact_pii(cls, before_when):
        queryset = cls.objects.filter(
            updated_at__lt=before_when, redacted_at=None
        ).all()
        paginator = Paginator(queryset, 200)
        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            updates = []
            for r in page.object_list:
                cls.redact(r)
                updates.append(r)
            cls.objects.bulk_update(
                updates,
                [
                    "registration",
                    "redacted_at",
                    "identification_found",
                    "ab_identification_found",
                ],
            )

    def to_dict(self):
        return {
            "registration": self.registration_as_dict(),
            "vr_completed_at": self.vr_completed_at,
            "ab_completed_at": self.ab_completed_at,
            "ref": self.ref,
            "is_citizen": self.is_citizen,
            "is_eighteen": self.is_eighteen,
            "dob_year": self.dob_year,
            "party": self.party,
            "county": self.county,
            "lang": self.lang,
            "signed_at": self.signed_at,
            "reg_lookup_complete": self.reg_lookup_complete,
            "addr_lookup_complete": self.addr_lookup_complete,
            "reg_found": self.reg_found,
            "identification_found": self.identification_found,
            "ab_identification_found": self.ab_identification_found,
        }

    def registration_as_dict(self):
        if not self.registration:
            return {}
        return json.loads(self.registration)

    def column_names(self):
        return [f.name for f in Registrant._meta.get_fields()]

    # update() is set_value() for a dict (bulk) to save encrypt/decrypt overhead
    def update(self, update_payload):
        rval = {}
        if self.registration:
            rval = self.registration_as_dict()
        for k, v in update_payload.items():
            if k in self.column_names():
                setattr(self, k, v)
            else:
                rval[k] = v
        self.registration = json.dumps(rval)

    def set_value(self, name, value):
        if name in self.column_names():
            return setattr(self, name, value)
        else:
            rval = {}
            if self.registration:
                rval = self.registration_as_dict()
            rval[name] = value
            self.registration = json.dumps(rval)
            return self

    def has_value_for_req(self, req):
        if req in self.column_names():
            if not getattr(self, req):
                return False
        else:
            if not self.registration_as_dict().get(req):
                return False
        return True

    def try_value(self, field_name, default_value=""):
        return self.registration_as_dict().get(field_name, default_value)

    def try_clerk(self):
        from ksvotes.models import Clerk

        return Clerk.find_by_county(self.county)

    def get_dob_year(self):
        dob_dt = datetime.strptime(self.try_value("dob"), "%m/%d/%Y")
        return int(dob_dt.year)

    def best_zip5(self):
        validated_addr = self.try_value("validated_addresses")
        if (
            validated_addr
            and "current_address" in validated_addr
            and "zip5" in validated_addr["current_address"]
        ):
            return validated_addr["current_address"]["zip5"]
        return self.try_value("zip")

    def precinct_address(self):
        parts = []
        parts.append(self.try_value("addr"))
        parts.append(self.try_value("city"))
        parts.append(self.try_value("state"))
        parts.append(self.try_value("zip"))
        return " ".join(parts)

    def middle_initial(self):
        middle_name = self.try_value("name_middle")
        if middle_name and len(middle_name) > 0:
            return middle_name[0]
        else:
            return None

    def name(self):
        return "{} {}".format(self.try_value("name_first"), self.try_value("name_last"))

    def updated_since(self, n_minutes):
        # returns boolean based on comparison of updated_at in last n_minutes
        since_last_updated = timezone.now() - self.updated_at
        window = timedelta(minutes=int(n_minutes))
        if since_last_updated > window:
            return False
        else:
            return True

    def elections(self):
        return self.try_value("elections").split("|")

    def sign_ab_forms(self):
        sig_string = self.try_value("signature_string", None)
        if not sig_string:
            return False

        from ksvotes.services.nvris_client import NVRISClient

        nvris_client = NVRISClient(self)
        ab_forms = []
        for election in self.elections():
            signed_ab_form = nvris_client.get_ab_form(election)
            if signed_ab_form:
                ab_forms.append(signed_ab_form)

        if len(ab_forms) > 0:
            self.update({"ab_forms": ab_forms})
            self.signed_at = timezone.now()

        return ab_forms

    def signed_at_central_tz(self):
        utc_tz = pytz.timezone("UTC")
        central_tz = pytz.timezone("US/Central")
        signed_at_utc = utc_tz.localize(self.signed_at)
        return signed_at_utc.astimezone(central_tz)

    def populate_address(self, sosrec):
        address = sosrec["Address"].replace("<br/>", " ")
        addr_parts = usaddress.tag(address)
        payload = {"addr": "", "unit": "", "city": "", "state": "KANSAS", "zip": ""}
        for key, val in addr_parts[0].items():
            if key == "OccupancyIdentifier":
                payload["unit"] = val
            elif key == "PlaceName":
                payload["city"] = val
            elif key == "StateName" and len(val) > 0:
                payload["state"] = val
            elif key == "ZipCode":
                payload["zip"] = val
            else:
                if len(payload["addr"]) > 0:
                    payload["addr"] = " ".join([payload["addr"], val])
                elif val == "No information available":
                    payload["addr"] = ""
                else:
                    payload["addr"] = val

        self.update(payload)

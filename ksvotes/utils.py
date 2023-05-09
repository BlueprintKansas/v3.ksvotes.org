# -*- coding: utf-8 -*-
import usaddress
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os
import re
import dateparser
from dateutil.parser import parse
from django.utils.translation import gettext_lazy as lazy_gettext
from wtforms.validators import DataRequired
import logging

logger = logging.getLogger(__name__)

COUNTIES = [
    "Allen",
    "Anderson",
    "Atchison",
    "Barber",
    "Barton",
    "Bourbon",
    "Brown",
    "Butler",
    "Chase",
    "Chautauqua",
    "Cherokee",
    "Cheyenne",
    "Clark",
    "Clay",
    "Cloud",
    "Coffey",
    "Comanche",
    "Cowley",
    "Crawford",
    "Decatur",
    "Dickinson",
    "Doniphan",
    "Douglas",
    "Edwards",
    "Elk",
    "Ellis",
    "Ellsworth",
    "Finney",
    "Ford",
    "Franklin",
    "Geary",
    "Gove",
    "Graham",
    "Grant",
    "Gray",
    "Greeley",
    "Greenwood",
    "Hamilton",
    "Harper",
    "Harvey",
    "Haskell",
    "Hodgeman",
    "Jackson",
    "Jefferson",
    "Jewell",
    "Johnson",
    "Kearny",
    "Kingman",
    "Kiowa",
    "Labette",
    "Lane",
    "Leavenworth",
    "Lincoln",
    "Linn",
    "Logan",
    "Lyon",
    "Marion",
    "Marshall",
    "McPherson",
    "Meade",
    "Miami",
    "Mitchell",
    "Montgomery",
    "Morris",
    "Morton",
    "Nemaha",
    "Neosho",
    "Ness",
    "Norton",
    "Osage",
    "Osborne",
    "Ottawa",
    "Pawnee",
    "Phillips",
    "Pottawatomie",
    "Pratt",
    "Rawlins",
    "Reno",
    "Republic",
    "Rice",
    "Riley",
    "Rooks",
    "Rush",
    "Russell",
    "Saline",
    "Scott",
    "Sedgwick",
    "Seward",
    "Shawnee",
    "Sheridan",
    "Sherman",
    "Smith",
    "Stafford",
    "Stanton",
    "Stevens",
    "Sumner",
    "Thomas",
    "Trego",
    "Wabaunsee",
    "Wallace",
    "Washington",
    "Wichita",
    "Wilson",
    "Woodson",
    "Wyandotte",
    "TEST",
]
KS_DL_PATTERN = r"^(\w\d\w\d\w|K\d\d-\d\d-\d\d\d\d|\d\d\d-\d\d-\d\d\d\d)$"

KS_TZ = ZoneInfo("America/Chicago")


def ks_today():
    return datetime.utcnow().astimezone(tz=KS_TZ).date()


def zip_code_matches(sosrec, zipcode):
    address = sosrec["Address"].replace("<br/>", " ")
    addr_parts = usaddress.tag(address)
    for key, val in addr_parts[0].items():
        if key == "ZipCode":
            if str(val).startswith(str(zipcode)):
                return True
    return False


def construct_county_choices(default):
    county_list = [("", "")]
    for county in COUNTIES:
        county_list.append((county, county))
    return county_list


def parse_election_date(election):
    pattern = r"(Primary|Primaria|General) \((.+)\)"
    m = re.match(pattern, str(election))
    if not m:
        return None
    date = m.group(2)
    return dateparser.parse(date)


def primary_election_active(deadline=None, current_time=None):
    """
    Determine if the primary election is active or not

    AB_PRIMARY_DEADLINE env var format is `YYYY-MM-DD HH:MM::SS` assuming a
    Central US time zone.
    """
    # Determine deadline from the environment
    if deadline is None:
        return False

    # Parse our deadline
    deadline_utc = parse(f"{deadline} CST", tzinfos={"CST": KS_TZ}).astimezone(
        timezone.utc
    )

    # Determine if we're past deadline
    if current_time is None:
        current_time = timezone.now()

    if current_time > deadline_utc:
        return False
    else:
        return True


def list_of_elections():
    elect_list = []

    # if we are before AB_PRIMARY_DEADLINE
    if primary_election_active(os.getenv("AB_PRIMARY_DEADLINE", None)):
        elect_list.append(
            (
                lazy_gettext("1AB_select_election_primary"),
                lazy_gettext("1AB_select_election_primary"),
            )
        )

    elect_list.append(
        (
            lazy_gettext("1AB_select_election_general"),
            lazy_gettext("1AB_select_election_general"),
        )
    )
    elect_list.append(("permanent", lazy_gettext("1AB_select_perm")))
    return elect_list


def is_even_year(year=None):
    """Determine if it's an even year"""
    if year is None:
        today = datetime.today()
        year = today.year

    if year % 2 == 0:
        return True
    else:
        return False


def str_to_bool(string):
    if isinstance(string, bool):
        return string
    if string == "True":
        return True
    else:
        return False


class RequiredIfBool(DataRequired):
    def __init__(self, check, *args, **kwargs):
        self.check = check
        super(RequiredIfBool, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        check_field = form._fields.get(self.check)
        logger.debug(
            "check_field={} value={} type={}".format(
                check_field, check_field.data, type(check_field.data)
            )
        )
        if check_field is None:
            raise Exception("invalid field" % self.check)
        if bool(check_field.data):
            super(RequiredIfBool, self).__call__(form, field)

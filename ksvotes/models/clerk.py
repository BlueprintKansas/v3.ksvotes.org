# -*- coding: utf-8 -*-
from .base import TimeStampedModel
from django.db import models
import csv
import re


class Clerk(TimeStampedModel):
    county = models.CharField(max_length=255, null=False)  # enum of ks counties
    officer = models.CharField(max_length=255, null=False)
    email = models.CharField(max_length=255, null=False)
    phone = models.CharField(max_length=255, null=False)  # formatted NNNNNNNNNN
    fax = models.CharField(max_length=255, null=False)  # formatted NNNNNNNNNN
    address1 = models.CharField(max_length=255, null=False)
    address2 = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=255, null=False)
    state = models.CharField(max_length=255, null=False, default="KS")
    zip = models.CharField(max_length=255, null=False)

    @classmethod
    def find_by_county(cls, county_name):
        if not county_name or len(county_name) == 0:
            return None
        return cls.objects.filter(county__iexact=county_name).first()

    @classmethod
    def find_or_create_by(cls, **kwargs):
        found_one = cls.objects.filter(**kwargs).first()
        if found_one:
            return found_one
        else:
            clerk = cls(**kwargs)
            return clerk

    @classmethod
    def load_fixtures(cls):
        csv_file = "county-clerks.csv"
        phone_re = re.compile(r"^(\d\d\d)(\d\d\d)(\d\d\d\d)$")
        with open(csv_file, newline="\n") as csvfile:
            next(csvfile)  # skip headers
            # GEOCODE_FORMAT,COUNTY,OFFICER,EMAIL,HOURS,PHONE,FAX,ADDRESS1,ADDRESS2,CITY,STATE,ZIP
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                ucfirst_county = row[1][0] + row[1][1:].lower()
                if ucfirst_county == "Mcpherson":
                    ucfirst_county = "McPherson"
                clerk = Clerk.find_or_create_by(county=ucfirst_county)
                clerk.officer = row[2]
                clerk.email = row[3]
                pm = phone_re.search(row[5])
                clerk.phone = "{area}-{f3}-{f4}".format(
                    area=pm.group(1), f3=pm.group(2), f4=pm.group(3)
                )
                fm = phone_re.search(row[6])
                clerk.fax = "{area}-{f3}-{f4}".format(
                    area=fm.group(1), f3=fm.group(2), f4=fm.group(3)
                )
                clerk.address1 = row[7]
                clerk.address2 = row[8]
                clerk.city = row[9]
                clerk.state = row[10]
                clerk.zip = row[11]
                clerk.save()

        # add the TEST fixture
        test_clerk = Clerk.find_or_create_by(county="TEST")
        test_clerk.email = "registration@ksvotes.org"
        test_clerk.phone = "test"
        test_clerk.fax = "test"
        test_clerk.officer = "test"
        test_clerk.address1 = "test"
        test_clerk.city = "test"
        test_clerk.state = "KS"
        test_clerk.zip = "test"
        test_clerk.save()

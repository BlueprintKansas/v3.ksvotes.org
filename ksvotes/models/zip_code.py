# -*- coding: utf-8 -*-
from .base import TimeStampedModel
from .clerk import Clerk
from django.db import models, connection, transaction
import csv


class ZIPCode(TimeStampedModel):
    zipcode = models.CharField(max_length=10, unique=True)
    counties = models.ManyToManyField("ZipCodeCounty", related_name="zip_codes")
    clerks = models.ManyToManyField(Clerk, through="ZipCodeCounty")

    @classmethod
    def find_by_zip5(cls, zip5):
        return cls.objects.filter(zipcode=zip5).first()

    @classmethod
    def guess_county(cls, zip5):
        z = cls.find_by_zip5(zip5)
        if not z:
            return None
        if z.counties.count() == 1:
            return z.counties.first().clerk.county

        # more than one county for this ZIP5.
        # sort the list by voter_count and pick the biggest.
        sorted_by_voter_count = sorted(
            z.counties.all(), key=lambda zc: zc.voter_count, reverse=True
        )
        return sorted_by_voter_count[0].clerk.county

    @classmethod
    def load_fixtures(cls, csv_file):
        cursor = connection.cursor()
        cursor.execute('TRUNCATE TABLE "ksvotes_zipcodecounty"')

        with open(csv_file, newline="\n") as csvfile:
            next(csvfile)  # skip headers
            # zip5,county_name,voter_count
            csvreader = csv.reader(csvfile)
            with transaction.atomic():
                for row in csvreader:
                    zip5 = row[0]
                    clerk = Clerk.find_by_county(row[1])
                    if not clerk:
                        raise Exception("Failed to find county for %s" % (row[1]))

                    z, _ = ZIPCode.objects.get_or_create(zipcode=zip5)
                    ZIPCodeCounty.objects.create(
                        voter_count=row[2], clerk=clerk, zipcode=z
                    )


class ZIPCodeCounty(TimeStampedModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["clerk_id", "zipcode_id"], name="clerk_zipcode_unique"
            )
        ]

    clerk = models.ForeignKey(Clerk, null=False, on_delete=models.CASCADE)
    zipcode = models.ForeignKey(ZIPCode, null=False, on_delete=models.CASCADE)
    voter_count = models.IntegerField(null=True)

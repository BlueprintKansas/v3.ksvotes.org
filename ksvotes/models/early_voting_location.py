# -*- coding: utf-8 -*-
from .base import TimeStampedModel
from django.db import models, connection, transaction
import csv
from ksvotes.utils import ks_today
import datetime


class FutureElectionManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(election_date__gte=ks_today())
            .order_by("polling_place_name")
        )


class EarlyVotingLocation(TimeStampedModel):
    class Meta:
        indexes = [
            models.Index(fields=["zipcode"]),
            models.Index(fields=["county"]),
            models.Index(fields=["polling_place_id"]),
        ]

    election_date = models.DateField(null=False)
    polling_place_id = models.IntegerField(null=True)
    polling_place_name = models.CharField(max_length=255, null=True)
    address1 = models.CharField(max_length=255, null=False)
    address2 = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=False)
    state = models.CharField(max_length=255, null=False, default="KS")
    zipcode = models.CharField(max_length=10, null=False)
    dropoff_type = models.CharField(max_length=255, null=True)
    ballot_drop_off = models.BooleanField(default=None, null=True)
    county = models.CharField(max_length=255, null=True)

    objects = models.Manager()
    future = FutureElectionManager()

    @classmethod
    def for_zip5(cls, zip5):
        return cls.future.filter(zipcode=zip5).all()

    @classmethod
    def for_county(cls, county):
        return cls.future.filter(county__iexact=county).all()

    @classmethod
    def load_fixtures(cls, csv_file):
        cursor = connection.cursor()
        cursor.execute(
            'TRUNCATE TABLE "ksvotes_earlyvotinglocation", "ksvotes_earlyvotinglocationhours"'
        )

        locations = {}

        with open(csv_file, newline="\n") as csvfile:
            next(csvfile)  # skip headers
            csvreader = csv.reader(csvfile)
            # election_name,election_day,polling_place_id,polling_place_name,address_line_1,address_line_2,city,state,zip,formatted_address,ballot_drop_off,dropoff_type,open_at,close_at,county_name
            with transaction.atomic():
                for row in csvreader:
                    location_id = row[2]
                    if location_id in locations:
                        evl = locations[location_id]
                    else:
                        evl = cls(
                            election_date=row[1].replace(" 0:00:00", ""),
                            polling_place_id=row[2],
                            polling_place_name=row[3],
                            address1=row[4],
                            address2=row[5],
                            city=row[6],
                            state=row[7],
                            zipcode=row[8],
                            ballot_drop_off=row[10].lower() == "true",
                            dropoff_type=row[11],
                            county=row[14].replace(" County", ""),
                        )
                        evl.save()
                        locations[location_id] = evl
                    hours = EarlyVotingLocationHours(
                        opens_at=datetime.datetime.strptime(
                            row[12] + "+0000", "%Y-%m-%d %H:%M:%S%z"
                        ),
                        closes_at=datetime.datetime.strptime(
                            row[13] + "+0000", "%Y-%m-%d %H:%M:%S%z"
                        ),
                        location=evl,
                    )
                    hours.save()

    @property
    def formatted_address(self):
        if self.address2:
            return f"{self.address1}, {self.address2}, {self.city}, {self.state} {self.zipcode}, USA"
        else:
            return f"{self.address1}, {self.city}, {self.state} {self.zipcode}, USA"

    @property
    def election_hours(self):
        return (
            self.earlyvotinglocationhours_set.filter(opens_at__date__gte=ks_today())
            .order_by("opens_at")
            .all()
        )


class EarlyVotingLocationHours(TimeStampedModel):
    class Meta:
        indexes = [
            models.Index(fields=["location"]),
        ]

    location = models.ForeignKey(
        EarlyVotingLocation, null=False, on_delete=models.CASCADE
    )
    opens_at = models.DateTimeField(default=None, null=True)
    closes_at = models.DateTimeField(default=None, null=True)

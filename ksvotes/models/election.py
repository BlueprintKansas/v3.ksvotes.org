# -*- coding: utf-8 -*-
from .base import TimeStampedModel
from django.db import models
import json
import dateparser
from datetime import timedelta, date
from ksvotes import utils


class Election(TimeStampedModel):
    name = models.CharField(max_length=255, null=False, unique=True)
    election_date = models.DateField(null=False)

    class ElectionType(models.TextChoices):
        GENERAL = "G"
        PRIMARY = "P"
        SPECIAL = "S"

    election_type = models.CharField(
        max_length=1,
        choices=ElectionType.choices,
        default=ElectionType.GENERAL,
    )

    vr_deadline = models.DateField(null=False)
    voting_start = models.DateField(null=False)
    ab_deadline = models.DateField(null=False)
    in_person_voting_start = models.DateField(null=False)

    class Meta:
        ordering = ["election_date"]  # queries always sort election_date asc

    @classmethod
    def find_or_create_by(cls, **kwargs):
        found_one = cls.objects.filter(**kwargs).first()
        if found_one:
            return found_one
        else:
            election = cls(**kwargs)
            return election

    @classmethod
    def upcoming(cls):
        # return the Election recs that will happen this year,
        # and are not in the past, relative to utils.ks_today()
        today = utils.ks_today()
        year = today.year
        year_end = date(year, 12, 31)
        return cls.objects.filter(
            election_date__gte=today,
            election_date__lt=year_end,
        ).all()

    @classmethod
    def load_fixtures(cls, json_file):
        with open(json_file, newline="\n") as fh:
            elections = json.load(fh)
            for e in elections:
                # some fields are required, and others can be inferred.
                election_date = e.get("electionDate")
                if not election_date:
                    raise ValueError(f"electionDate missing in {e}")
                election_date = dateparser.parse(election_date)
                election_type = e.get("type", "General")
                if election_type not in [et.label for et in cls.ElectionType]:
                    raise ValueError("type must be General, Primary or Special")
                election_type = cls.ElectionType[election_type.upper()]
                name = e.get("name", f"{election_type.label} {election_date.year}")

                election = Election.find_or_create_by(name=name)
                election.election_date = election_date

                vr_deadline = e.get("vrDeadline")
                if not vr_deadline:
                    raise ValueError("vrDeadline missing in {e}")

                election.vr_deadline = dateparser.parse(vr_deadline)

                election.voting_start = e.get(
                    "votingStart",
                    (election.vr_deadline + timedelta(days=1)).strftime("%Y-%m-%d"),
                )
                election.ab_deadline = e.get(
                    "abDeadline",
                    (election.vr_deadline + timedelta(days=14)).strftime("%Y-%m-%d"),
                )
                election.in_person_voting_start = e.get(
                    "inPersonVotingStart", election.ab_deadline
                )

                election.save()

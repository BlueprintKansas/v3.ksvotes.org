# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from ksvotes.models import EarlyVotingLocation


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = settings.BASE_DIR.joinpath(
            "ksvotes", "early-voting-locations.csv"
        ).as_posix()
        EarlyVotingLocation.load_fixtures(csv_file)

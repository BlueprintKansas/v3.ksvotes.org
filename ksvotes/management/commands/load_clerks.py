# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from ksvotes.models import Clerk


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = settings.BASE_DIR.joinpath("ksvotes", "county-clerks.csv").as_posix()
        Clerk.load_fixtures(csv_file)

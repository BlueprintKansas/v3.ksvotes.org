# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from ksvotes.models import ZIPCode


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = settings.BASE_DIR.joinpath(
            "ksvotes", "ks-zip-by-county.csv"
        ).as_posix()
        ZIPCode.load_fixtures(csv_file)

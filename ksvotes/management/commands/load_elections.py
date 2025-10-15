# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from ksvotes.models import Election


class Command(BaseCommand):
    def handle(self, *args, **options):
        json_file = settings.BASE_DIR.joinpath("ksvotes", "elections.json").as_posix()
        Election.load_fixtures(json_file)

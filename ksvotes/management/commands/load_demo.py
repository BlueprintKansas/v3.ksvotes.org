# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from ksvotes.models import Registrant


class Command(BaseCommand):
    def handle(self, *args, **options):
        Registrant.load_fixtures()

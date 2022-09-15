# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from ksvotes.models import Registrant
from datetime import datetime, timedelta
import os


class Command(BaseCommand):
    help = "Redact sensitive PII from recent Registrants"

    def add_arguments(self, parser):
        parser.add_argument(
            "--older", nargs=1, type=str, help="redact records older than N days"
        )

    def handle(self, *args, **options):
        redact_older_than = int(os.getenv("REDACT_OLDER_THAN_DAYS", 2))
        if options["older"]:
            redact_older_than = int(options["older"][0])
        days_ago = timedelta(days=redact_older_than)
        Registrant.redact_pii(datetime.utcnow() - days_ago)

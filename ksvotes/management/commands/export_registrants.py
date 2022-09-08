# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from ksvotes.models import Registrant
from ksvotes.services.registrant_exporter import RegistrantExporter

CHUNK_SIZE = 200


class Command(BaseCommand):
    help = "Export Registrants, decrypted, in CSV format"

    def add_arguments(self, parser):
        parser.add_argument(
            "--since", nargs=1, type=str, help="export records on or after <date>"
        )

    def handle(self, *args, **options):
        if options["since"]:
            regs = Registrant.objects.filter(
                Registrant.updated_at > options["since"][0]
            ).iterator(chunk_size=CHUNK_SIZE)
        else:
            regs = Registrant.objects.iterator(chunk_size=CHUNK_SIZE)
        exporter = RegistrantExporter(regs)
        exporter.export()

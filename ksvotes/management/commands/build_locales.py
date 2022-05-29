# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
import json
import os
import os.path


class Command(BaseCommand):
    def handle(self, *args, **options):
        en_file = settings.BASE_DIR.joinpath(
            "ksvotes", "locale", "en", "LC_MESSAGES", "django.po"
        ).as_posix()
        es_file = settings.BASE_DIR.joinpath(
            "ksvotes", "locale", "es", "LC_MESSAGES", "django.po"
        ).as_posix()
        if not os.path.exists(os.path.dirname(en_file)):
            os.makedirs(os.path.dirname(en_file))
        if not os.path.exists(os.path.dirname(es_file)):
            os.makedirs(os.path.dirname(es_file))
        if os.path.exists(en_file):
            os.remove(en_file)
        if os.path.exists(es_file):
            os.remove(es_file)
        en_po = open(en_file, "w")
        es_po = open(es_file, "w")

        comment = '# DO NOT EDIT - edit translations.json instead\n\nmsgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8"\n\n'
        en_po.write(comment)
        es_po.write(comment)

        with open(
            settings.BASE_DIR.joinpath("ksvotes", "translations.json").as_posix()
        ) as jsonfile:
            translations = json.load(jsonfile)
            for msgid in sorted(translations):
                entry = translations[msgid]
                en_txt = entry["en"]
                es_txt = entry["es"]
                en_po.write('msgid "%s"\n' % (msgid))
                es_po.write('msgid "%s"\n' % (msgid))
                en_po.write(
                    'msgstr "%s"\n\n'
                    % (en_txt.replace("\n", "\\n").replace('"', '\\"'))
                )
                es_po.write(
                    'msgstr "%s"\n\n'
                    % (es_txt.replace("\n", "\\n").replace('"', '\\"'))
                )

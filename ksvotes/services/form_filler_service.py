# -*- coding: utf-8 -*-
import os
import requests
import json
from urllib.parse import urlparse
import base64
import logging
import subprocess
from django.conf import settings

logger = logging.getLogger(__name__)


class FormFillerService:

    FORMS = {
        "/vr/en": {
            "definitions": "form-defs/VREN.json",
            "base": "https://s3.amazonaws.com/ksvotes-v2/FEDVRENNVRIS-v2.png",
        },
        "/vr/es": {
            "definitions": "form-defs/VRES.json",
            "base": "https://s3.amazonaws.com/ksvotes-v2/FEDVRENNVRIS_SP-v2.png",
        },
        "/av/ksav1/en": {
            "definitions": "form-defs/KSAV1.json",
            "base": "https://s3.amazonaws.com/ksvotes-v2/AV1M.png",
        },
        "/av/ksav2/en": {
            "definitions": "form-defs/KSAV2.json",
            "base": "https://s3.amazonaws.com/ksvotes-v2/AV2.png",
        },
        "/av/ksav1/es": {
            "definitions": "form-defs/AV1M_SP.json",
            "base": "https://s3.amazonaws.com/ksvotes-v2/AV1M_SP.png",
        },
        "/av/ksav2/es": {
            "definitions": "form-defs/AV2_SP.json",
            "base": "https://s3.amazonaws.com/ksvotes-v2/AV2_SP.png",
        },
    }

    def __init__(self, payload, form_name):
        self.payload = payload
        self.form_name = form_name
        self.debug = os.getenv("FORM_DEBUG")

        self.__run_filler()

    def __get_definitions(self):
        def_file = settings.BASE_DIR.joinpath(
            "ksvotes", self.FORMS[self.form_name]["definitions"]
        ).as_posix()
        logger.info(
            "{} loading {} form defs from {}".format(
                self.payload["uuid"], self.form_name, def_file
            )
        )
        return def_file

    def __get_payload_path(self):
        digest = self.payload["uuid"]
        payload_path = f"/tmp/{digest}.json"
        with open(payload_path, "w") as f:
            json.dump(self.payload, f)
        return payload_path

    def __get_image(self):
        url = self.FORMS[self.form_name]["base"]
        logger.info(
            "{} loading {} image from {}".format(
                self.payload["uuid"], self.form_name, url
            )
        )
        img_base_name = os.path.basename(urlparse(url).path)
        cache_name = f"/tmp/{img_base_name}"
        if not os.path.exists(cache_name):
            self.__fetch_image(url, cache_name)
        return cache_name

    def __fetch_image(self, url, cache_name):
        img = requests.get(url)
        with open(cache_name, "wb") as f:
            f.write(img.content)

    def __run_filler(self):
        defs = self.__get_definitions()
        img = self.__get_image()
        payload_path = self.__get_payload_path()
        cmd = [
            "python",
            "-m",
            "formfiller",
            f"--payload={payload_path}",
            f"--form={defs}",
            f"--image={img}",
        ]
        proc = subprocess.run(cmd, capture_output=True)
        if proc.returncode == 0:
            self.filled_form = base64.b64encode(proc.stdout)
            if not self.debug:
                os.remove(payload_path)
        else:
            logger.error(
                "{} failed to fill form: {}".format(self.payload["uuid"], proc.stderr)
            )
            self.filled_form = False

    def as_image(self):
        if not self.filled_form:
            raise ValueError("Failed to complete form")
        return "data:image/png;base64," + self.as_base64()

    def as_base64(self):
        if not self.filled_form:
            raise ValueError("Failed to complete form")
        return self.filled_form.decode()

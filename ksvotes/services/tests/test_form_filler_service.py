# -*- coding: utf-8 -*-
import json
import re
import base64
from ksvotes.services.form_filler_service import FormFillerService
import logging

logger = logging.getLogger(__name__)


def test_vr_en_form():
    payload_file = "ksvotes/services/tests/test-vr-en-payload.json"
    with open(payload_file) as payload_f:
        payload = json.load(payload_f)

        ffs = FormFillerService(payload=payload, form_name="/vr/en")
        img = ffs.as_image()
        logger.info("got image:{}".format(img))
        matches = re.fullmatch(r"(data:image\/(.+?);base64),(.+)", img, re.I)

        assert matches.group(1) == "data:image/png;base64"
        assert matches.group(2) == "png"
        assert base64.b64decode(matches.group(3))

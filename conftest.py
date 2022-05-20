# -*- coding: utf-8 -*-
import pytest
from django.conf import settings
from ksvotes.models import Clerk, Registrant, ZIPCode
import os
from unittest import mock


@pytest.fixture(scope="session", autouse=True)
@mock.patch.dict(os.environ, {"DEMO_UUID": "e39966ee8a23441fb4adc257233b617f"})
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        Clerk.load_fixtures(
            settings.BASE_DIR.joinpath("ksvotes", "county-clerks.csv").as_posix()
        )
        ZIPCode.load_fixtures(
            settings.BASE_DIR.joinpath("ksvotes", "ks-zip-by-county.csv").as_posix()
        )
        Registrant.load_fixtures()

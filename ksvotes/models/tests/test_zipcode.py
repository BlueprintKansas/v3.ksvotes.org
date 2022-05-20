# -*- coding: utf-8 -*-
import pytest
from ksvotes.models import ZIPCode


@pytest.mark.django_db
def test_zipcode():
    z = ZIPCode.find_by_zip5("66044")
    assert z.counties.count() == 3
    assert ZIPCode.guess_county("66044") == "Douglas"

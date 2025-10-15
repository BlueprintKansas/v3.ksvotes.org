# -*- coding: utf-8 -*-
from ksvotes.utils import is_even_year


def test_is_even_year():
    assert is_even_year(year=2018)
    assert not is_even_year(year=2019)

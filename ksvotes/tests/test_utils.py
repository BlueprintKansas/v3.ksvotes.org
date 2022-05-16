# -*- coding: utf-8 -*-
from ksvotes.utils import zip_code_matches


def test_zip_code_matches():
    sosrec = {"Address": "123 Main St #456 Wichita, KS, 12345-9999"}

    assert zip_code_matches(sosrec, 12345) == True
    assert zip_code_matches(sosrec, "12345") == True
    assert zip_code_matches(sosrec, 98765) == False
    assert zip_code_matches(sosrec, 9999) == False
    assert zip_code_matches(sosrec, "myzip") == False

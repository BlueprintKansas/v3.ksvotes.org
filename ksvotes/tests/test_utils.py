# -*- coding: utf-8 -*-
from ksvotes.utils import zip_code_matches
from test_plus import TestCase
from django.conf import settings


class KSVotesTestCase(TestCase):
    def update_session(self, registrant):
        session = self.client.session
        session["id"] = str(registrant.session_id)
        session.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key
        return session


def test_zip_code_matches():
    sosrec = {"Address": "123 Main St #456 Wichita, KS, 12345-9999"}

    assert zip_code_matches(sosrec, 12345) == True
    assert zip_code_matches(sosrec, "12345") == True
    assert zip_code_matches(sosrec, 98765) == False
    assert zip_code_matches(sosrec, 9999) == False
    assert zip_code_matches(sosrec, "myzip") == False

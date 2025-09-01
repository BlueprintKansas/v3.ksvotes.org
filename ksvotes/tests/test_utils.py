# -*- coding: utf-8 -*-
from ksvotes.utils import zip_code_matches, list_of_elections
import pytest
from test_plus import TestCase
from django.conf import settings
from ksvotes.models import Election
from unittest import mock
from datetime import date


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


@pytest.mark.django_db
def test_list_of_elections():
    json_file = settings.BASE_DIR.joinpath("ksvotes", "elections.json").as_posix()
    Election.load_fixtures(json_file)

    with mock.patch("ksvotes.utils.ks_today") as mock_today:
        mock_today.return_value = date(2025, 7, 30)  # day after ab deadline
        elections = list_of_elections()
        assert len(elections) == 2
        key, label = elections[0]
        assert "General" in label

    with mock.patch("ksvotes.utils.ks_today") as mock_today:
        mock_today.return_value = date(2025, 7, 29)  # day of ab deadline
        elections = list_of_elections()
        assert len(elections) == 3
        key, label = elections[0]
        assert "Primary" in label
        key2, label2 = elections[1]
        assert "General" in label2

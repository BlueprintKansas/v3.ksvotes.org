# -*- coding: utf-8 -*-
from test_plus import TestCase
from ksvotes.models import Election
from datetime import date
from unittest import mock


class ElectionTestCase(TestCase):
    def test_upcoming(self):
        with mock.patch("ksvotes.utils.ks_today") as mock_today:
            mock_today.return_value = date(2025, 9, 1)
            upcoming = Election.upcoming()
            self.assertEqual(1, len(upcoming), "only General upcoming")
            self.assertEqual("General 2025", upcoming[0].name)
        with mock.patch("ksvotes.utils.ks_today") as mock_today:
            mock_today.return_value = date(2025, 6, 1)
            upcoming = Election.upcoming()
            self.assertEqual(2, len(upcoming), "Primary and General upcoming")
            self.assertEqual("Primary 2025", upcoming[0].name)
            self.assertEqual("General 2025", upcoming[1].name)

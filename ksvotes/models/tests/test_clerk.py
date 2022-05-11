# -*- coding: utf-8 -*-
from test_plus import TestCase
from ksvotes.models import Clerk


class ClerkTestCase(TestCase):
    def test_find_by_county(self):
        Clerk.objects.create(
            county="foo",
            officer="bar",
            email="foo@bar.com",
            phone="5555555555",
            fax="5555555555",
            address1="123 fake st",
            address2="ste 107",
            city="springfield",
            state="KANSAS",
            zip="55555",
        )
        clerk = Clerk.find_by_county("foo")
        assert clerk.officer == "bar"

# -*- coding: utf-8 -*-
import pytest
from ksvotes.models import EarlyVotingLocation


@pytest.mark.django_db
def test_evl():
    evls = EarlyVotingLocation.for_zip5("66044")
    assert len(evls) == 2
    evls = EarlyVotingLocation.for_county("Douglas")
    assert evls[0].county == "Douglas"
    # TODO test .election_hours by mocking data and "today"

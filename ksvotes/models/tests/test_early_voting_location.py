# -*- coding: utf-8 -*-
import pytest
import datetime
from ksvotes.models import EarlyVotingLocation
from unittest.mock import patch

TODAY = datetime.datetime(2022, 10, 31, 0, 0, 0).date()
DAY_AFTER_ELECTION = datetime.datetime(2022, 11, 9, 0, 0, 0).date()


@pytest.mark.django_db
def test_evl():
    with patch("ksvotes.models.early_voting_location.ks_today") as mock_today:
        mock_today.return_value = TODAY
        evls = EarlyVotingLocation.for_zip5("66044")
        assert len(evls) == 2
        evls = EarlyVotingLocation.for_county("Douglas")
        assert evls[0].county == "Douglas"
        assert (
            evls[0].polling_place_name == "Douglas County Courthouse (Dropbox outside)"
        )
        assert evls[0].election_hours.count() == 1
        assert evls[2].polling_place_name == "Lied Center Pavilion"
        assert evls[2].election_hours.count() == 2

    with patch("ksvotes.models.early_voting_location.ks_today") as mock_today:
        mock_today.return_value = DAY_AFTER_ELECTION
        evls = EarlyVotingLocation.for_county("Douglas")
        assert len(evls) == 0

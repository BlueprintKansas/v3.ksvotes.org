# -*- coding: utf-8 -*-
from ksvotes.models import Registrant
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.steps import Step_0, Step_VR_1
from django.utils import timezone
import pytest


def create_registrant():
    r = Registrant()
    r.update({"name_first": "foo"})
    r.save()
    return r


@pytest.mark.django_db
def test_non_previous_step_non_complete_step():
    """
    A non complete step should return the current steps endpoint
    """
    registrant = create_registrant()
    step = Step_0()
    session_manager = SessionManager(registrant, step)
    assert session_manager.get_redirect_url() == step.endpoint


@pytest.mark.django_db
def test_no_previous_step_is_complete():
    """
    A complete step should return the next steps endpoint
    """
    registrant = create_registrant()
    step = Step_0()
    # mock step actions
    step.is_complete = True
    step.next_step = "Step_VR_1"

    session_manager = SessionManager(registrant, step)
    assert session_manager.get_redirect_url() == "/vr/citizenship/"


@pytest.mark.django_db
def test_registrant_doesnt_have_values():
    """
    A registrant should be redirected to previous step if missing values of that step
    """
    registrant = create_registrant()
    form_payload = {"is_citizen": True}
    step = Step_VR_1(form_payload)
    step.run()

    session_manager = SessionManager(registrant, step)
    assert session_manager.get_redirect_url() == "/"


@pytest.mark.django_db
def test_completion_logic():
    registrant = create_registrant()
    step = Step_0()
    session_manager = SessionManager(registrant, step)
    assert session_manager.vr_completed() == False
    assert session_manager.ab_completed() == False

    registrant.vr_completed_at = timezone.now()
    registrant.update({"vr_form": "foobar"})
    registrant.save()
    session_manager = SessionManager(registrant, step)
    assert session_manager.vr_completed() == True
    assert session_manager.ab_completed() == False

    registrant.update({"ab_forms": "foobar"})
    registrant.save()
    session_manager = SessionManager(registrant, step)
    assert session_manager.vr_completed() == True
    assert session_manager.ab_completed() == False

    registrant.ab_completed_at = timezone.now()
    registrant.save()
    session_manager = SessionManager(registrant, step)
    assert session_manager.vr_completed() == True
    assert session_manager.ab_completed() == True

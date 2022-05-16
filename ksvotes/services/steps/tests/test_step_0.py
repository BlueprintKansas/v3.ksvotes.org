# -*- coding: utf-8 -*-
from ksvotes.services.steps import Step_0


def test_step_0_is_complete_false():
    """
    Verify that this registrant is not ready to move on to the next step.

    """
    form_payload = {"name_first": "foo"}
    step = Step_0(form_payload)
    assert step.run() == False
    assert step.is_complete == False
    assert step.next_step == None


def test_step_0_is_complete_true_and_none_registered():
    form_payload = {
        "name_first": "foo",
        "name_last": "bar",
        "dob": "01/01/2000",
        "email": "foo@example.com",
        "zip": "12345",
    }
    step = Step_0(form_payload)
    assert step.run() == True
    assert step.is_complete == True
    assert step.next_step == "Step_1"


def test_step_0_is_complete_true_and_already_registered():
    """
    Verify that next step is AB 1
    """
    form_payload = {
        "name_first": "Kris",
        "name_last": "Kobach",
        "dob": "03/26/1966",
        "email": " foo@example.com",
        "zip": "66044",
    }
    step = Step_0(form_payload)
    assert step.run() == True
    assert step.is_complete == True
    assert step.next_step == "Step_1"

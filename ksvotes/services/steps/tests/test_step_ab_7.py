# -*- coding: utf-8 -*-
from ksvotes.services.steps import Step_AB_7


def test_step_ab7_is_complete_false():
    form_payload = {}
    step = Step_AB_7(form_payload)
    assert step.run() == False
    assert step.is_complete == False
    assert step.next_step == None


def test_step_ab7_is_complete_true():
    form_payload = {"affirmation": True}
    step = Step_AB_7(form_payload)
    assert step.run() == True
    assert step.is_complete == True
    assert step.next_step == "Step_AB_8"

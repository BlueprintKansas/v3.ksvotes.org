# -*- coding: utf-8 -*-
from ksvotes.services.steps import Step_AB_1
from ksvotes.models import Registrant
from django.utils import timezone


def test_step_ab1_is_complete_false():
    form_payload = {}
    registrant = Registrant()
    step = Step_AB_1(form_payload, registrant)
    assert step.run() == False
    assert step.is_complete == False
    assert step.next_step == None


def test_step_ab1_is_complete_true():
    form_payload = {"elections": "General (November 6, 2018)"}
    registrant = Registrant()
    step = Step_AB_1(form_payload, registrant)
    assert step.run() == True
    assert step.is_complete == True
    assert step.next_step == "Step_AB_3"


def test_step_ab1_is_complete_with_registrant_skips_address():
    form_payload = {"elections": "General (November 6, 2018)"}
    registrant = Registrant(vr_completed_at=timezone.now())
    step = Step_AB_1(form_payload, registrant)
    assert step.run() == True
    assert step.is_complete == True
    assert step.next_step == "Step_AB_5"

# -*- coding: utf-8 -*-
from ksvotes.services.steps import Step_VR_3


def test_step_vr3_is_complete_false_with_missing_arguments():
    form_payload = {}
    step = Step_VR_3(form_payload)
    assert step.run() == False
    assert step.is_complete == False
    assert step.next_step == None


def test_step_vr3_is_complete_true_with_one_address():
    form_payload = {
        "addr": "707 Vermont St",
        "unit": "Room A",
        "city": "Lawrence",
        "state": "KANSAS",
        "zip": "66044",
    }
    step = Step_VR_3(form_payload)
    step.run()
    assert step.run() == True
    assert step.is_complete == True

    expected = {
        "current_address": {
            "address": "707 VERMONT ST",
            "city": "LAWRENCE",
            "error": None,
            "state": "KS",
            "unit": "RM A",
            "zip4": "2371",
            "zip5": "66044",
        }
    }
    assert expected == step.validated_addresses
    assert step.addr_lookup_complete == True
    assert step.next_step == "Step_VR_4"


def test_step_vr3_is_complete_false_with_bad_address():
    form_payload = {
        "addr": "123 Fake St",
        "city": "Fake",
        "state": "NA",
        "zip": "66044",
    }
    step = Step_VR_3(form_payload)
    step.run()
    assert step.validated_addresses == False
    assert step.is_complete == True
    assert step.addr_lookup_complete == True


def test_step_vr3_with_prev_address():
    form_payload = {
        "addr": "707 Vermont St",
        "unit": "Room A",
        "city": "Lawrence",
        "state": "KANSAS",
        "zip": "66044",
        "has_prev_addr": True,
        "prev_addr": "707 Vermont St",
        "prev_unit": "Room B",
        "prev_city": "Lawrence",
        "prev_state": "KANSAS",
        "prev_zip": "66044",
    }
    step = Step_VR_3(form_payload)
    step.run()
    assert step.is_complete == True
    assert step.next_step == "Step_VR_4"
    expected = {
        "current_address": {
            "address": "707 VERMONT ST",
            "city": "LAWRENCE",
            "error": None,
            "state": "KS",
            "unit": "RM A",
            "zip4": "2371",
            "zip5": "66044",
        },
        "prev_addr": {
            "address": "707 VERMONT ST",
            "city": "LAWRENCE",
            "error": None,
            "state": "KS",
            "unit": "RM B",
            "zip4": "2371",
            "zip5": "66044",
        },
    }
    assert expected == step.validated_addresses
    assert step.addr_lookup_complete == True


def test_step_vr3_with_bad_prev_address():
    form_payload = {
        "addr": "707 Vermont St",
        "unit": "Room A",
        "city": "Lawrence",
        "state": "KANSAS",
        "zip": "66044",
        "has_prev_addr": True,
        "prev_addr": "foo",
        "prev_unit": "bar",
        "prev_city": "baz",
        "prev_state": "nitro",
        "prev_zip": "",
    }
    step = Step_VR_3(form_payload)
    step.run()
    assert step.is_complete == True
    assert step.next_step == "Step_VR_4"
    expected = {
        "current_address": {
            "address": "707 VERMONT ST",
            "city": "LAWRENCE",
            "error": None,
            "state": "KS",
            "unit": "RM A",
            "zip4": "2371",
            "zip5": "66044",
        },
        "prev_addr": {"error": "There was an issue validating your address."},
    }
    assert expected == step.validated_addresses


def test_step_vr3_with_errors():
    form_payload3 = {
        "addr": "707 Vermont St",
        "unit": "Room A",
        "city": "Lawrence",
        "state": "KANSAS",
        "zip": "66044",
        "has_prev_addr": True,
        "prev_addr": "456 Any St",
        "prev_unit": "Apt A",
        "prev_city": "Some Place",
        "prev_state": "MO",
        "prev_zip": "12345-1234",
        "has_mail_addr": True,
        "mail_addr": "999 Mailing Ave",
        "mail_unit": "Apt B",
        "mail_city": "Specific City",
        "mail_state": "NE",
        "mail_zip": "12345-1234",
    }
    step = Step_VR_3(form_payload3)
    step.run()
    assert step.is_complete == True
    assert step.next_step == "Step_VR_4"
    expected = {
        "current_address": {
            "address": "707 VERMONT ST",
            "city": "LAWRENCE",
            "error": None,
            "state": "KS",
            "unit": "RM A",
            "zip4": "2371",
            "zip5": "66044",
        },
        "mail_addr": {"error": "There was an issue validating your address."},
        "prev_addr": {"error": "There was an issue validating your address."},
    }
    assert expected == step.validated_addresses


def test_step_vr3_with_prev_address_and_mail_addr():
    form_payload3 = {
        "addr": "707 Vermont St",
        "unit": "Room A",
        "city": "Lawrence",
        "state": "KANSAS",
        "zip": "66044",
        "has_prev_addr": True,
        "prev_addr": "707 Vermont St",
        "prev_unit": "Room B",
        "prev_city": "Lawrence",
        "prev_state": "KANSAS",
        "prev_zip": "66044",
        "has_mail_addr": True,
        "mail_addr": "707 Vermont St",
        "mail_unit": "Room C",
        "mail_city": "Lawrence",
        "mail_state": "KANSAS",
        "mail_zip": "66044",
    }
    step = Step_VR_3(form_payload3)
    step.run()
    assert step.is_complete == True
    assert step.next_step == "Step_VR_4"
    expected = {
        "current_address": {
            "address": "707 VERMONT ST",
            "city": "LAWRENCE",
            "error": None,
            "state": "KS",
            "unit": "RM A",
            "zip4": "2371",
            "zip5": "66044",
        },
        "mail_addr": {
            "address": "707 VERMONT ST",
            "city": "LAWRENCE",
            "error": None,
            "state": "KS",
            "unit": "RM C",
            "zip4": "2371",
            "zip5": "66044",
        },
        "prev_addr": {
            "address": "707 VERMONT ST",
            "city": "LAWRENCE",
            "error": None,
            "state": "KS",
            "unit": "RM B",
            "zip4": "2371",
            "zip5": "66044",
        },
    }
    assert expected == step.validated_addresses
    assert step.addr_lookup_complete == True

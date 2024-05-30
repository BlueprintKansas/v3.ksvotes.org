# -*- coding: utf-8 -*-
from django.urls import reverse
from django.utils.translation import gettext_lazy as lazy_gettext


def steps(request):
    flows = {
        "ab": {
            1: reverse("ksvotes-i18n:ab.election_picker"),
            2: reverse("ksvotes-i18n:ab.address"),
            3: reverse("ksvotes-i18n:ab.identification"),
            4: reverse("ksvotes-i18n:ab.preview"),
            5: reverse("ksvotes-i18n:ab.affirmation"),
            6: reverse("ksvotes-i18n:ab.submission"),
        },
        "vr": {
            1: reverse("ksvotes-i18n:vr.citizenship"),
            2: reverse("ksvotes-i18n:vr.name"),
            3: reverse("ksvotes-i18n:vr.address"),
            4: reverse("ksvotes-i18n:vr.party"),
            5: reverse("ksvotes-i18n:vr.identification"),
            6: reverse("ksvotes-i18n:vr.preview"),
            7: reverse("ksvotes-i18n:vr.affirmation"),
            8: reverse("ksvotes-i18n:vr.submission"),
        },
    }
    if "/ab/" in request.path:
        flow_flavor = "ab"
    else:
        flow_flavor = "vr"
    return {
        "error": None,
        "next_btn": None,
        "next_btn_selector": None,
        "disabled_btn": None,
        "submit_btn": None,
        "cancel_btn": None,
        "registrant": None,
        "current_step": None,
        "previous_step_url": None,
        "flow_flavor": flow_flavor,
        "flows": flows,
        "flow_map": flows[flow_flavor],
        "total_steps": len(flows[flow_flavor]),
        "step_range": range(1, len(flows[flow_flavor])),
        "register_link": lazy_gettext("1AB_sorry_no_reg_link"),
    }

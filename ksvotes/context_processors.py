# -*- coding: utf-8 -*-
from django.urls import reverse
from django.utils.translation import gettext_lazy as lazy_gettext


def steps(request):
    flows = {
        "ab": {
            1: reverse("ksvotes:ab.election_picker"),
            2: reverse("ksvotes:ab.address"),
            3: reverse("ksvotes:ab.identification"),
            4: reverse("ksvotes:ab.preview"),
            5: reverse("ksvotes:ab.affirmation"),
            6: reverse("ksvotes:ab.submission"),
        },
        "vr": {
            1: reverse("ksvotes:vr.citizenship"),
            2: reverse("ksvotes:vr.name"),
            3: reverse("ksvotes:vr.address"),
            4: reverse("ksvotes:vr.party"),
            5: reverse("ksvotes:vr.identification"),
            6: reverse("ksvotes:vr.preview"),
            7: reverse("ksvotes:vr.affirmation"),
            8: reverse("ksvotes:vr.submission"),
        },
    }
    if "/ab/" in request.path:
        flow_flavor = "ab"
    else:
        flow_flavor = "vr"
    return {
        "next_btn": None,
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

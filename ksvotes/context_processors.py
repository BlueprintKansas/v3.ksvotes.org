# -*- coding: utf-8 -*-
from django.urls import reverse


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
    if "/vr" in request.path:
        flow_flavor = "vr"
    else:
        flow_flavor = "ab"
    return {
        "flows": flows,
        "flow_map": flows[flow_flavor],
        "total_steps": len(flows[flow_flavor]),
        "step_range": range(1, len(flows[flow_flavor])),
    }

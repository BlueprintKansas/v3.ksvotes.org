# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse
from ksvotes.forms.step_0 import FormStep0
import logging
import datetime
from ksvotes.services.registrant_stats import RegistrantStats
from ksvotes.services.early_voting_locations import EarlyVotingLocations
from ksvotes.services.dropboxes import Dropboxes
from ksvotes.models import Clerk

logger = logging.getLogger(__name__)


def stats(request):  # TODO
    ninety_days = datetime.timedelta(days=90)
    today = datetime.date.today()
    s = RegistrantStats()
    vr_stats = s.vr_through_today(today - ninety_days)
    ab_stats = s.ab_through_today(today - ninety_days)

    stats = {"vr": [], "ab": []}
    for r in vr_stats:
        stats["vr"].append(r.values())
    for r in ab_stats:
        stats["ab"].append(r.values())

    return render(request, "stats.html", {"stats": stats})


def terms(request):
    return render(request, "terms.html")


def privacy(request):
    return render(request, "privacy-policy.html")


def about(request):
    return render(request, "about.html")


def change_or_apply(request):
    reg = request.registrant
    sos_reg = reg.try_value("sos_reg")
    skip_sos = reg.try_value("skip_sos")
    sos_failure = reg.try_value("sos_failure")
    county = reg.county
    if not county and sos_reg:
        county = sos_reg[0]["tree"]["County"]
    clerk = None
    evl = None
    dropboxes = None
    if county:
        clerk = Clerk.find_by_county(county)
        evl = EarlyVotingLocations(county).locations
        dropboxes = Dropboxes(county).dropboxes

    return render(
        request,
        "change-or-apply.html",
        {
            "skip_sos": skip_sos,
            "sos_reg": sos_reg,
            "sos_failure": sos_failure,
            "clerk": clerk,
            "early_voting_locations": evl,
            "dropboxes": dropboxes,
        },
    )


class HomepageView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["use_hero"] = True
        context["form"] = FormStep0()
        return context

    def post(self, request, *args, **kwargs):
        form = FormStep0(request.POST)
        if form.validate():
            r = request.registrant
            r.update(form.data)
            # zipcode = form.data.get("zip")
            # save what we know so far
            r.save()
            # look up registration is we need to.
            return redirect(reverse("ksvotes:home.change_or_apply"))
        else:
            return HttpResponse()  # TODO populate form

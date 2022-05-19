# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, Http404
from django.conf import settings
from django.utils.translation import get_language
from ksvotes.forms.step_0 import FormStep0
from ksvotes.services.steps import Step_0
from ksvotes.services.session_manager import SessionManager
import logging
import datetime
from uuid import uuid4
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
            "precinct_address": reg.precinct_address(),
        },
    )


def demo(request):
    if settings.DEMO_UUID:
        logger.debug("loading demo fixture")
        request.session["id"] = settings.DEMO_UUID
    return redirect("/ref/?ref=demo")


def referring_org(request):
    # we will accept whatever subset of step0 fields are provided.
    # we always start a new session, but we require a 'ref' code.
    if not request.GET.get("ref"):
        raise Http404("404 Not Found")

    ref = request.GET["ref"]

    if request.method == "GET":
        request.session["ref"] = ref
        return redirect("/")

    # special 'ref' value of 'demo' attaches to the DEMO_UUID if defined
    if ref == "demo" and settings.DEMO_UUID:
        logger.debug("loading demo fixture")
        request.session["id"] = settings.DEMO_UUID
    else:
        request.session["id"] = str(uuid4())
        registrant = Registrant(session_id=request.session["id"], ref=ref)
        registration = {
            "name_last": request.GET.get("name_last", ""),
            "name_first": request.GET.get("name_first", ""),
            "dob": request.GET.get("dob", ""),
            "email": request.GET.get("email", ""),
            "phone": request.GET.get("phone", ""),
            "zip": request.GET.get("zip", ""),
        }
        registrant.update(registration)
        registrant.save()

    return redirect("/")


def debug(request):
    this_session = {
        "_session_key": request.session.session_key,
    }
    for k in request.session.keys():
        this_session[k] = request.session[k]
    if hasattr(request, "registrant"):
        this_session["registrant"] = request.registrant.as_dict()
    return JsonResponse(this_session)


class HomepageView(TemplateView):
    template_name = "index.html"

    def get_form(self):
        if hasattr(self.request, "registrant"):
            registrant = self.request.registrant
            return FormStep0(
                ref=self.request.GET.get("ref", self.request.session.get("ref")),
                name_first=registrant.try_value("name_first"),
                name_last=registrant.try_value("name_last"),
                dob=registrant.try_value("dob"),
                zip=registrant.try_value("zip"),
                email=registrant.try_value("email"),
                phone=registrant.try_value("phone"),
            )
        else:
            return FormStep0(
                ref=self.request.GET.get("ref", self.request.session.get("ref"))
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["use_hero"] = True
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = FormStep0(request.POST)
        if form.validate():
            step = Step_0(form.data)
            if hasattr(request, "registrant"):
                registrant = request.registrant
            else:
                zipcode = form.data.get("zip")
                sid = str(uuid4())
                registrant = Registrant(
                    county=ZIPCode.guess_county(zipcode),
                    ref=form.data.get("ref"),
                    session_id=sid,
                    lang=get_language(),
                )
                request.session["id"] = sid

            registrant.update(form.data)
            skip_sos = request.GET.get("skip-sos")
            step.run(skip_sos)
            registrant.reg_lookup_complete = step.reg_lookup_complete
            registrant.reg_found = True if step.reg_found else False
            registrant.dob_year = registrant.get_dob_year()
            sos_reg = None
            sos_failure = None
            if step.reg_found:
                sos_reg = []
                for rec in step.reg_found:
                    rec2save = {"tree": rec["tree"]}
                    if "sample_ballots" in rec:
                        rec2save["sample_ballot"] = rec["sample_ballots"]
                    if "districts" in rec:
                        rec2save["districts"] = rec["districts"]
                    if "elections" in rec:
                        rec2save["elections"] = rec["elections"]
                    if "polling" in rec:
                        rec2save["polling"] = rec["polling"]

                    # prepopulate address and party, if possible
                    try:
                        registrant.populate_address(rec2save["tree"])
                    except Exception as err:
                        # just log errors for now
                        logger.exception(err)

                    sos_reg.append(rec2save)
            else:
                sos_failure = step.voter_view_fail

            registrant.update(
                {"sos_reg": sos_reg, "skip_sos": skip_sos, "sos_failure": sos_failure}
            )
            registrant.save()

            # small optimization for common case.
            if skip_sos and not settings.ENABLE_AB:
                return redirect("/vr/citizenship")

            session_manager = SessionManager(registrant, step)
            return redirect(session_manager.get_redirect_url())

        return HttpResponse()
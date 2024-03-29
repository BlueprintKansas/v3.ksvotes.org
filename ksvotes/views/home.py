# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.http import HttpResponse, JsonResponse, Http404, QueryDict
from django.conf import settings
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils.translation import gettext_lazy as lazy_gettext
from ksvotes.views.step_view import StepView
from ksvotes.forms.step_0 import FormStep0
from ksvotes.services.steps import Step_0
from ksvotes.services.session_manager import SessionManager
import logging
import datetime
from uuid import uuid4
from ksvotes.services.registrant_stats import RegistrantStats
from ksvotes.services.ksvotes_redis import KSVotesRedis
from ksvotes.models import Clerk, Registrant, ZIPCode, EarlyVotingLocation

logger = logging.getLogger(__name__)


def stats(request):
    span = request.GET.get("span", "30")
    span_days = datetime.timedelta(days=int(span))
    if request.GET.get("end"):
        end_date = datetime.datetime.fromisoformat(request.GET.get("end"))
    else:
        end_date = datetime.datetime.now()
    s = RegistrantStats()
    vr_stats = s.vr_through_today(end_date - span_days, end_date)
    ab_stats = s.ab_through_today(end_date - span_days, end_date)
    reg_lookups = s.reg_lookups(end_date - span_days, end_date)
    reg_success = s.reg_lookups_successful(end_date - span_days, end_date)

    stats = {"vr": [], "ab": [], "reg": [], "reg_success": []}
    for r in vr_stats:
        stats["vr"].append(r)
    for r in ab_stats:
        stats["ab"].append(r)
    for r in reg_lookups:
        stats["reg"].append(r)
    for r in reg_success:
        stats["reg_success"].append(r)

    return render(request, "stats.html", {"stats": stats})


def clerk_details(request, county):
    clerk = Clerk.find_by_county(county)
    if clerk:
        evls = EarlyVotingLocation.for_county(county)
        return render(
            request,
            "county.html",
            {
                "clerk": clerk,
                "early_voting_locations": evls,
            },
        )
    else:
        raise Http404


def api_total_processed(request):
    s = RegistrantStats()
    r = KSVotesRedis()

    def get_vr_total():
        return s.vr_total_processed()

    def get_ab_total():
        return s.ab_total_processed()

    # cache for 1 hour
    ttl = 60 * 60
    reg_count = int(r.get_or_set("vr-total-processed", get_vr_total, ttl))
    ab_count = int(r.get_or_set("ab-total-processed", get_ab_total, ttl))
    return JsonResponse({"registrations": reg_count, "advanced_ballots": ab_count})


def terms(request):
    return render(request, "terms.html")


def privacy(request):
    return render(request, "privacy-policy.html")


def about(request):
    return render(request, "about.html")


@never_cache
def change_or_apply(request):
    reg = request.registrant
    sos_reg = reg.try_value("sos_reg")
    skip_sos = reg.try_value("skip_sos")
    sos_failure = reg.try_value("sos_failure")
    county = reg.county
    if not county and sos_reg:
        county = sos_reg[0]["tree"]["County"]
    clerk = None
    evls = None
    if county:
        clerk = Clerk.find_by_county(county)
        evls = EarlyVotingLocation.for_county(county)

    return render(
        request,
        "change-or-apply.html",
        {
            "skip_sos": skip_sos,
            "sos_reg": sos_reg,
            "sos_failure": sos_failure,
            "clerk": clerk,
            "early_voting_locations": evls,
            "precinct_address": reg.precinct_address(),
        },
    )


@require_http_methods(["POST"])
@never_cache
def change_county(request):
    reg = request.registrant
    existing_county = reg.county
    new_county = request.POST.get("county")
    redirect_url = request.POST.get("return")

    if not redirect_url:
        redirect_url = reverse("ksvotes-i18n:home.index")

    if redirect_url.startswith("ksvotes:"):
        redirect_url = reverse(redirect_url)

    if not new_county or new_county == existing_county:
        logger.error("unable to change county")
        redirect(redirect_url)

    logger.debug("new county %s return to %s" % (new_county, redirect_url))
    reg.county = new_county

    # must invalidate any cached images since county is on the forms
    if reg.try_value("ab_forms"):
        reg.sign_ab_forms()
        messages.info(request, lazy_gettext("ab_forms_county_changed"))

    reg.save()

    return redirect(redirect_url)


@require_http_methods(["GET", "POST"])
@never_cache
def forget(request):
    request.session.flush()
    return redirect(reverse("ksvotes-i18n:home.index"))


@never_cache
def demo(request):
    if settings.DEMO_UUID:
        logger.debug("loading demo fixture via /demo")
        # always reset values as well
        Registrant.load_fixtures()
        request.session["id"] = settings.DEMO_UUID
    return referring_org_redirect(request, "demo")


@csrf_exempt
@never_cache
def referring_org(request):
    # we will accept whatever subset of step0 fields are provided.
    # we always start a new session, but we require a 'ref' code.
    if not request.GET.get("ref"):
        logger.debug("missing ref param, language={}".format(get_language()))
        raise Http404("404 Not Found")

    ref = request.GET["ref"]

    home_page_url = reverse("ksvotes-i18n:home.index")

    if request.method == "GET":
        request.session["ref"] = ref
        return redirect(home_page_url)

    # special 'ref' value of 'demo' attaches to the DEMO_UUID if defined
    if ref == "demo" and settings.DEMO_UUID:
        logger.debug("loading demo fixture")
        request.session["id"] = settings.DEMO_UUID
    else:
        request.session["id"] = str(uuid4())
        registrant = Registrant(session_id=request.session["id"], ref=ref)
        registration = {}
        for p in ["name_last", "name_first", "dob", "email", "phone", "zip"]:
            registration[p] = request.GET.get(p, request.POST.get(p, ""))
        registrant.update(registration)
        registrant.save()
    return redirect(home_page_url)


@never_cache
def referring_org_redirect(request, refcode):
    query = QueryDict("", mutable=True)
    query.update({"ref": refcode})
    url = "{base}?{query}".format(
        base=reverse("ksvotes-i18n:home.ref"), query=query.urlencode()
    )
    return redirect(url)


@never_cache
def debug(request):
    this_session = {
        "_session_key": request.session.session_key,
    }
    for k in request.session.keys():
        this_session[k] = request.session[k]
    if hasattr(request, "registrant"):
        this_session["registrant"] = request.registrant.as_dict()
    return JsonResponse(this_session)


class HomepageView(StepView):
    template_name = "index.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form(self):
        if hasattr(self.request, "registrant"):
            registrant = self.request.registrant
            return FormStep0(
                ref=(
                    registrant.ref
                    if registrant.ref
                    else self.request.GET.get("ref", self.request.session.get("ref"))
                ),
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
            skip_sos = request.GET.get("skip-sos", request.POST.get("skip-sos"))
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
                    rec2save["sample_ballot"] = rec.get("sample_ballots")
                    rec2save["districts"] = rec.get("districts")
                    rec2save["elections"] = rec.get("elections")
                    rec2save["polling"] = rec.get("polling")

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
            registrant.user_agent = request.headers.get("user-agent")
            if sos_reg:
                registrant.county = sos_reg[0]["tree"]["County"]
            registrant.save()

            # small optimization for common case.
            if skip_sos and not settings.ENABLE_AB:
                return redirect(reverse("ksvotes-i18n:vr.citizenship"))

            session_manager = SessionManager(registrant, step)
            return redirect(session_manager.get_redirect_url())

        return HttpResponse()

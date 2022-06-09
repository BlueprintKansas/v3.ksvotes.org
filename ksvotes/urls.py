# -*- coding: utf-8 -*-
from django.urls import path
from .views import home
from .views.vr.citizenship import VR1View
from .views.vr.name import VR2View
from .views.vr.address import VR3View
from .views.vr.party import VR4View
from .views.vr.identification import VR5View
from .views.vr.preview_sign import VR6View
from .views.vr.affirmation import VR7View
from .views.vr.submission import VR8View
from .views.ab.election_picker import AB1View
from .views.ab.address import AB3View
from .views.ab.identification import AB5View
from .views.ab.preview_sign import AB6View
from .views.ab.affirmation import AB7View
from .views.ab.submission import AB8View

urlpatterns = [
    path("", home.HomepageView.as_view(), name="home.index"),
    # with and w/o trailing slash
    path("ref/", home.referring_org, name="home.ref"),
    path("ref", home.referring_org, name="home.ref_v2"),
    path("r/<refcode>/", home.referring_org_redirect, name="home.ref_v2_redirect"),
    path("api/total-processed/", home.api_total_processed, name="api.total_processed"),
    path("demo/", home.demo, name="home.demo"),
    path("debug/", home.debug, name="home.debug"),
    path("terms/", home.terms, name="home.terms"),
    path("about/", home.about, name="home.about"),
    path("privacy-policy/", home.privacy, name="home.privacy"),
    path("change-or-apply/", home.change_or_apply, name="home.change_or_apply"),
    path("change-county/", home.change_county, name="home.change_county"),
    path("forget/", home.forget, name="home.forget"),
    path("stats/", home.stats, name="home.stats"),
    path("county/<county>/", home.clerk_details, name="home.county"),
    # underscore path backcompat for v2
    path("ab/election_picker/", AB1View.as_view(), name="ab.election_picker_v2"),
    path("ab/election-picker/", AB1View.as_view(), name="ab.election_picker"),
    path("ab/address/", AB3View.as_view(), name="ab.address"),
    path("ab/identification/", AB5View.as_view(), name="ab.identification"),
    path("ab/preview/", AB6View.as_view(), name="ab.preview"),
    path("ab/affirmation/", AB7View.as_view(), name="ab.affirmation"),
    path("ab/submission/", AB8View.as_view(), name="ab.submission"),
    path("vr/citizenship/", VR1View.as_view(), name="vr.citizenship"),
    path("vr/name/", VR2View.as_view(), name="vr.name"),
    path("vr/address/", VR3View.as_view(), name="vr.address"),
    path("vr/party/", VR4View.as_view(), name="vr.party"),
    path("vr/identification/", VR5View.as_view(), name="vr.identification"),
    path("vr/preview/", VR6View.as_view(), name="vr.preview"),
    path("vr/affirmation/", VR7View.as_view(), name="vr.affirmation"),
    path("vr/submission/", VR8View.as_view(), name="vr.submission"),
]

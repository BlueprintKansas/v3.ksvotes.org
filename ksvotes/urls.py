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

urlpatterns = [
    path("", home.HomepageView.as_view(), name="home.index"),
    path("ref/", home.referring_org, name="home.ref"),
    path("demo/", home.demo, name="home.demo"),
    path("debug/", home.debug, name="home.debug"),
    path("terms/", home.terms, name="home.terms"),
    path("about/", home.about, name="home.about"),
    path("privacy-policy/", home.privacy, name="home.privacy"),
    path("change-or-apply/", home.change_or_apply, name="home.change_or_apply"),
    path("change-county/", home.change_county, name="home.change_county"),
    path("forget/", home.forget, name="home.forget"),
    path("ab/election-picker/", home.privacy, name="ab.election_picker"),  # TODO
    path("ab/address/", home.privacy, name="ab.address"),  # TODO
    path("ab/identification/", home.privacy, name="ab.identification"),  # TODO
    path("ab/preview/", home.privacy, name="ab.preview"),  # TODO
    path("ab/affirmation/", home.privacy, name="ab.affirmation"),  # TODO
    path("ab/submission/", home.privacy, name="ab.submission"),  # TODO
    path("vr/citizenship/", VR1View.as_view(), name="vr.citizenship"),
    path("vr/name/", VR2View.as_view(), name="vr.name"),
    path("vr/address/", VR3View.as_view(), name="vr.address"),
    path("vr/party/", VR4View.as_view(), name="vr.party"),
    path("vr/identification/", VR5View.as_view(), name="vr.identification"),
    path("vr/preview/", VR6View.as_view(), name="vr.preview"),
    path("vr/affirmation/", VR7View.as_view(), name="vr.affirmation"),
    path("vr/submission/", VR8View.as_view(), name="vr.submission"),
]

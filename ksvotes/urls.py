# -*- coding: utf-8 -*-
from django.urls import path
from .views import home
from .views.vr.citizenship import VR1View

urlpatterns = [
    path("", home.HomepageView.as_view(), name="home.index"),
    path("ref/", home.referring_org, name="home.ref"),
    path("demo/", home.demo, name="home.demo"),
    path("debug/", home.debug, name="home.debug"),
    path("terms/", home.terms, name="home.terms"),
    path("about/", home.about, name="home.about"),
    path("privacy-policy/", home.privacy, name="home.privacy"),
    path("change-or-apply/", home.change_or_apply, name="home.change_or_apply"),
    path("ab/election-picker/", home.privacy, name="ab.election_picker"),  # TODO
    path("ab/address/", home.privacy, name="ab.address"),  # TODO
    path("ab/identification/", home.privacy, name="ab.identification"),  # TODO
    path("ab/preview/", home.privacy, name="ab.preview_sign"),  # TODO
    path("ab/affirmation/", home.privacy, name="ab.affirmation"),  # TODO
    path("ab/submission/", home.privacy, name="ab.submission"),  # TODO
    path("vr/citizenship/", VR1View.as_view(), name="vr.citizenship"),
    path("vr/name/", home.privacy, name="vr.name"),  # TODO
    path("vr/address/", home.privacy, name="vr.address"),  # TODO
    path("vr/party/", home.privacy, name="vr.party"),  # TODO
    path("vr/identification/", home.privacy, name="vr.identification"),  # TODO
    path("vr/preview/", home.privacy, name="vr.preview_sign"),  # TODO
    path("vr/affirmation/", home.privacy, name="vr.affirmation"),  # TODO
    path("vr/submission/", home.privacy, name="vr.submission"),  # TODO
]

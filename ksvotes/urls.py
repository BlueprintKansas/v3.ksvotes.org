# -*- coding: utf-8 -*-
from django.urls import path
from .views import home

urlpatterns = [
    path("", home.HomepageView.as_view(), name="home.index"),
    path("terms/", home.terms, name="home.terms"),
    path("about/", home.about, name="home.about"),
    path("privacy-policy/", home.privacy, name="home.privacy"),
]

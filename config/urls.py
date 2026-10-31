# -*- coding: utf-8 -*-
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from .views import health_check
from ak.views import (
    ForbiddenView,
    InternalServerErrorView,
    NotFoundView,
    OKView,
)

urlpatterns = [
    path("", include(("ksvotes.urls", "ksvotes"), namespace="ksvotes")),
    path(
        "favicon.ico", RedirectView.as_view(url="/static/img/favicon/favicon-96x96.png")
    ),
    path("robots.txt", RedirectView.as_view(url="/static/robots.txt")),
    path("health", health_check, name="health_check"),
    path("200", OKView.as_view(), name="ok"),
    path("403", ForbiddenView.as_view(), name="forbidden"),
    path("404", NotFoundView.as_view(), name="not_found"),
    path("500", InternalServerErrorView.as_view(), name="internal_server_error"),
]

urlpatterns += i18n_patterns(
    path("", include(("ksvotes.urls", "ksvotes"), namespace="ksvotes-i18n")),
)

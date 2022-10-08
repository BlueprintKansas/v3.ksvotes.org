# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from rest_framework import routers
from users.views import UserViewSet, CurrentUserView
from ak.views import (
    ForbiddenView,
    InternalServerErrorView,
    NotFoundView,
    OKView,
)

router = routers.SimpleRouter()

router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(("ksvotes.urls", "ksvotes"), namespace="ksvotes")),
    path("admin/", admin.site.urls),
    path("users/me/", CurrentUserView.as_view(), name="current-user"),
    re_path(r"^api/v1/", include(router.urls)),
    path(
        "favicon.ico", RedirectView.as_view(url="/static/img/favicon/favicon-96x96.png")
    ),
    path("robots.txt", RedirectView.as_view(url="/static/robots.txt")),
    path("200", OKView.as_view(), name="ok"),
    path("403", ForbiddenView.as_view(), name="forbidden"),
    path("404", NotFoundView.as_view(), name="not_found"),
    path("500", InternalServerErrorView.as_view(), name="internal_server_error"),
    # path("health/", include("health_check.urls")),
]

urlpatterns += i18n_patterns(
    path("", include(("ksvotes.urls", "ksvotes"), namespace="ksvotes-i18n")),
)

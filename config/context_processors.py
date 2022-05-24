# -*- coding: utf-8 -*-
from django.conf import settings
import os
import logging
from django.utils import translation
from django.utils.translation import gettext_lazy as lazy_gettext

logger = logging.getLogger(__name__)


def base_url(request):  # pragma: no cover
    base_url = f"{request.scheme}://{request.get_host()}"
    return {
        "base_url": base_url,
        "current_path": request.path,
    }


# initialize common vars to None to sidestep VariableDoesNotExist
# errors, even when the vars are not used.
def common_vars(request):
    params = {
        "DEBUG": settings.DEBUG,
        "GIT_SHA": os.environ.get("GIT_SHA", "set GIT_SHA env var"),
        "GA_KEY": os.environ.get("GA_KEY", None),
        "STAGE_BANNER": os.environ.get("STAGE_BANNER", None),
        "ENABLE_AB": settings.ENABLE_AB,
        "ENABLE_AB_TRACKER": settings.ENABLE_AB_TRACKER,
        "locale": translation.get_language(),
        "browser_ua": None,  # TODO
        "has_announcements": lazy_gettext("announce") != "announce",
        "use_hero": False,
        "SESSION_TTL": settings.SESSION_TTL,
        "ENABLE_VOTING_LOCATION": settings.ENABLE_VOTING_LOCATION,
    }
    return params

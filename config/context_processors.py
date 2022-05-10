# -*- coding: utf-8 -*-
from django.conf import settings
import os
import logging
from django.utils import translation

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
        "GIT_SHA": os.environ.get("GIT_SHA", "set GIT_SHA env var"),
        "GA_KEY": os.environ.get("GA_KEY", None),
        "STAGE_BANNER": os.environ.get("STAGE_BANNER", None),
        "ENABLE_AB": os.environ.get("ENABLE_AB", None),
        "locale": translation.get_language(),
        "SESSION_TTL": settings.SESSION_TTL,
    }
    return params

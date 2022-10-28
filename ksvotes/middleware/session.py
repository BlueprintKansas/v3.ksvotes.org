# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as lazy_gettext
from uuid import uuid4
from ksvotes.models import Registrant
import logging
from django.utils import timezone
from ksvotes.utils import KS_TZ

logger = logging.getLogger(__name__)

REGISTRANT_SESSION_REQUIRED = [
    "/vr/",
    "/ab/",
    "/change-",
    "/forget/",
]


class SessionTimeout(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # always assume Central timezone for rendering dates/times
        timezone.activate(KS_TZ)

        current_lang = get_language()
        request_path = request.path.replace(f"/{current_lang}/", "/")
        logger.debug(
            "current_language={} path={} request_path={}".format(
                current_lang, request.path, request_path
            )
        )
        if request_path in REGISTRANT_SESSION_REQUIRED:
            return self.require_session(request, request_path)

        for path in REGISTRANT_SESSION_REQUIRED:
            if request_path.startswith(path):
                return self.require_session(request, request_path)

        # root page is a little tricky since we want autofill to work for ref etc.
        if request.session.get("id") and request_path == "/":
            return self.require_session(request, request_path)

        return self.get_response(request)

    def require_session(self, request, request_path):
        existing_session = request.session.get("id")
        session_id = request.session.get("id", str(uuid4()))
        registrant, is_new = Registrant.objects.get_or_create(session_id=session_id)
        request.session["id"] = session_id

        if request_path != "/":
            if is_new:
                logger.debug("redirect to flow start")
                messages.warning(request, lazy_gettext("session_interrupted_error"))
                if existing_session:
                    request.session.flush()
                return redirect(reverse("ksvotes-i18n:home.index"))

            # we must have *some* registration info if we are beyond the root (step_0) page.
            if len(registrant.registration_as_dict()) == 0:
                logger.debug("empty registration -- redirect to /")
                return redirect(reverse("ksvotes-i18n:home.index"))

        # Security belt-and-suspenders. Disallow session continuation if the Registrant
        # has not been updated within the SESSION_TTL window.
        if (
            not registrant.updated_since(settings.SESSION_TTL)
            and not registrant.is_demo()
        ):
            logger.error("Discontinuing old session for existing Registrant")
            messages.warning(request, lazy_gettext("session_interrupted_error"))
            request.session.flush()
            return redirect(reverse("ksvotes-i18n:home.index"))

        request.registrant = registrant
        return self.get_response(request)

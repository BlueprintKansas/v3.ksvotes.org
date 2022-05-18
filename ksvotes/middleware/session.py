# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as lazy_gettext
from uuid import uuid4
from ksvotes.models import Registrant
import logging

logger = logging.getLogger(__name__)

REGISTRANT_SESSION_REQUIRED = [
    "/vr/",
    "/ab/",
    "/change-or-apply/",
    "/ref/",
    "/debug/",
]


class SessionTimeout(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in REGISTRANT_SESSION_REQUIRED:
            return self.require_session(request)

        for path in REGISTRANT_SESSION_REQUIRED:
            if request.path.startswith(path):
                return self.require_session(request)

        # root page is a little tricky since we want autofill to work for ref etc.
        if request.session.get("id") and request.path == "/":
            return self.require_session(request)

        return self.get_response(request)

    def require_session(self, request):
        existing_session = request.session.get("id")
        session_id = request.session.get("id", str(uuid4()))
        registrant, is_new = Registrant.objects.get_or_create(session_id=session_id)
        request.session["id"] = session_id

        if request.path != "/":
            if is_new:
                logger.debug("redirect to flow start")
                messages.warning(request, lazy_gettext("session_interrupted_error"))
                if existing_session:
                    request.session.flush()
                return redirect("/")

            # we must have *some* registration info if we are beyond the root (step_0) page.
            if len(registrant.registration_as_dict()) == 0:
                logger.debug("empty registration -- redirect to /")
                return redirect("/")

        # Security belt-and-suspenders. Disallow session continuation if the Registrant
        # has not been updated within the SESSION_TTL window.
        if (
            not registrant.updated_since(settings.SESSION_TTL)
            and not registrant.is_demo()
        ):
            logger.error("Discontinuing old session for existing Registrant")
            messages.warning(request, lazy_gettext("session_interrupted_error"))
            request.session.flush()
            return redirect("/")

        request.registrant = registrant
        return self.get_response(request)

# -*- coding: utf-8 -*-
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.steps import Step_VR_7  # previous step
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
import logging

logger = logging.getLogger(__name__)


class VR8View(TemplateView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        reg = request.registrant
        session_manager = SessionManager(reg, Step_VR_7())
        if not session_manager.vr_completed():
            return redirect(session_manager.get_redirect_url())
        clerk = reg.try_clerk()
        return render(
            request, "vr/submission.html", {"registrant": reg, "clerk": clerk}
        )

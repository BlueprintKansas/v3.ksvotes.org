# -*- coding: utf-8 -*-
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.steps import Step_AB_7  # previous step
from ksvotes.views.step_view import StepView
from django.shortcuts import redirect, render
import logging

logger = logging.getLogger(__name__)


class AB8View(StepView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        reg = request.registrant
        session_manager = SessionManager(reg, Step_AB_7())
        if not session_manager.ab_completed():
            return redirect(session_manager.get_redirect_url())
        clerk = reg.try_clerk()
        return render(
            request, "ab/submission.html", {"registrant": reg, "clerk": clerk}
        )

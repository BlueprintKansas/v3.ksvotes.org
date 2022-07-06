# -*- coding: utf-8 -*-
from ksvotes.forms.vr_1 import FormVR1
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.steps import Step_VR_1
from ksvotes.views.step_view import StepView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class VR1View(StepView):
    template_name = "vr/citizenship.html"

    def get_form(self):
        reg = self.request.registrant
        return FormVR1(
            is_citizen=reg.is_citizen,
            is_eighteen=reg.is_eighteen,
        )

    def post(self, request, *args, **kwargs):
        form = FormVR1(request.POST)
        if form.validate():
            step = Step_VR_1(form.data)
            if step.run():
                r = request.registrant
                r.update(form.data)
                r.save()
                session_manager = SessionManager(r, step)
                return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormVR1 failed to validate: {}".format(form.errors))

        # if anything failed to validate or run, re-render
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs) | {"form": form},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["current_step"] = 1
        context["previous_step_url"] = reverse("ksvotes:home.index")
        return context

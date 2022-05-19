# -*- coding: utf-8 -*-
from ksvotes.forms.vr_5 import FormVR5
from ksvotes.services.steps import Step_VR_5
from ksvotes.services.session_manager import SessionManager
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class VR5View(TemplateView):
    template_name = "vr/identification.html"

    def get_form(self):
        reg = self.request.registrant
        return FormVR5(
            identification=reg.try_value("identification", ""),
        )

    def post(self, request, *args, **kwargs):
        form = FormVR5(request.POST)
        if form.validate():
            step = Step_VR_5(form.data)
            step.run()
            request.registrant.update(form.data)
            request.registrant.save()
            session_manager = SessionManager(request.registrant, step)
            return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormVR3 failed to validate: {}".format(form.errors))

        # if anything failed to validate or run, re-render
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs) | {"form": form},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["current_step"] = 5
        context["previous_step_url"] = reverse("ksvotes:vr.party")
        return context

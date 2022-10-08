# -*- coding: utf-8 -*-
from ksvotes.forms.vr_4 import FormVR4
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.steps import Step_VR_4
from ksvotes.views.step_view import StepView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class VR4View(StepView):
    template_name = "vr/party.html"

    def get_form(self):
        reg = self.request.registrant
        return FormVR4(
            party=reg.party,
        )

    def post(self, request, *args, **kwargs):
        form = FormVR4(request.POST)
        if form.validate():
            step = Step_VR_4(form.data)
            step.run()
            request.registrant.update(form.data)
            request.registrant.save()
            session_manager = SessionManager(request.registrant, step)
            return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormVR4 failed to validate: {}".format(form.errors))

        # if anything failed to validate or run, re-render
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs) | {"form": form},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["current_step"] = 4
        context["previous_step_url"] = reverse("ksvotes-i18n:vr.address")
        context["usps_fields"] = ["address", "unit", "city", "state", "zip5"]
        context["validated_addresses"] = self.request.registrant.try_value(
            "validated_addresses"
        )
        return context

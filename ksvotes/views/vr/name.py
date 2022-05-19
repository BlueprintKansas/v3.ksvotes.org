# -*- coding: utf-8 -*-
from ksvotes.forms.vr_2 import FormVR2
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.steps import Step_VR_2
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class VR2View(TemplateView):
    template_name = "vr/name.html"

    def get_form(self):
        reg = self.request.registrant
        return FormVR2(
            prefix=reg.try_value("prefix", ""),
            name_first=reg.try_value("name_first", ""),
            name_middle=reg.try_value("name_middle", ""),
            name_last=reg.try_value("name_last", ""),
            suffix=reg.try_value("suffix", ""),
            has_prev_name=reg.try_value("has_prev_name", ""),
            prev_prefix=reg.try_value("prev_prefix", ""),
            prev_name_first=reg.try_value("prev_name_first", ""),
            prev_name_middle=reg.try_value("prev_name_middle", ""),
            prev_name_last=reg.try_value("prev_name_last", ""),
            prev_suffix=reg.try_value("prev_suffix", ""),
        )

    def post(self, request, *args, **kwargs):
        form = FormVR2(request.POST)
        if form.validate():
            step = Step_VR_2(form.data)
            step.run()
            request.registrant.update(form.data)
            request.registrant.save()
            session_manager = SessionManager(request.registrant, step)
            return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormVR2 failed to validate: {}".format(form.errors))

        # if anything failed to validate or run, re-render
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs) | {"form": form},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["current_step"] = 2
        context["previous_step_url"] = reverse("ksvotes:vr.citizenship")
        return context

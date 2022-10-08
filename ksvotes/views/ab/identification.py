# -*- coding: utf-8 -*-
from ksvotes.forms.ab_5 import FormAB5
from ksvotes.services.steps import Step_AB_5
from ksvotes.services.session_manager import SessionManager
from ksvotes.views.step_view import StepView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class AB5View(StepView):
    template_name = "ab/identification.html"

    def get_form(self):
        return FormAB5(
            ab_identification=self.request.registrant.try_value("ab_identification")
        )

    def get(self, request, *args, **kwargs):
        # skip if permanent AB application
        if request.registrant.ab_permanent:
            return redirect(reverse("ksvotes-i18n:ab.preview"))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = FormAB5(request.POST)
        if form.validate():
            step = Step_AB_5(form.data)
            if step.run():
                request.registrant.update(form.data)
                request.registrant.save()
                session_manager = SessionManager(request.registrant, step)
                return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormAB5 failed to validate: {}".format(form.errors))

        # if anything failed to validate or run, re-render
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs) | {"form": form},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["current_step"] = 3
        context["previous_step_url"] = reverse("ksvotes-i18n:ab.address")
        context["clerk"] = self.request.registrant.try_clerk()
        return context

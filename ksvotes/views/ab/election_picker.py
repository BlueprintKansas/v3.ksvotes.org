# -*- coding: utf-8 -*-
from ksvotes.forms.ab_1 import FormAB1
from ksvotes.services.steps import Step_AB_1
from ksvotes.utils import list_of_elections, is_even_year
from ksvotes.services.session_manager import SessionManager
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class AB1View(TemplateView):
    template_name = "ab/election_picker.html"

    def get_form(self):
        reg = self.request.registrant
        form = FormAB1(
            party=reg.try_value("party"), perm_reason=reg.try_value("perm_reason")
        )
        # must assign at run time for date math.
        form.elections.choices = list_of_elections()
        form.elections.data = reg.elections()
        return form

    def post(self, request, *args, **kwargs):
        form = FormAB1(request.POST)
        reg = request.registrant
        if form.validate():
            step = Step_AB_1(form.data)
            if step.run():
                reg.update(form.data)

                if "permanent" in reg.elections():
                    reg.ab_permanent = True
                else:
                    reg.ab_permanent = False

                reg.save()
                session_manager = SessionManager(reg, step)
                return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormAB1 failed to validate: {}".format(form.errors))

        # if anything failed to validate or run, re-render
        # must assign at run time for date math.
        form.elections.choices = list_of_elections()
        form.elections.data = reg.elections()
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
        context["is_even_year"] = is_even_year()
        return context

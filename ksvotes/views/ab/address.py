# -*- coding: utf-8 -*-
from ksvotes.forms.ab_3 import FormAB3
from ksvotes.services.steps import Step_AB_3
from ksvotes.services.session_manager import SessionManager
from ksvotes.models import ZIPCode
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class AB3View(TemplateView):
    template_name = "ab/address.html"

    def get_form(self):
        reg = self.request.registrant
        return FormAB3(
            addr=reg.try_value("addr"),
            unit=reg.try_value("unit"),
            city=reg.try_value("city"),
            state=reg.try_value("state", "KANSAS"),
            zip=reg.try_value("zip"),
            has_mail_addr=reg.try_value("has_mail_addr"),
            mail_addr=reg.try_value("mail_addr"),
            mail_unit=reg.try_value("mail_unit"),
            mail_city=reg.try_value("mail_city"),
            mail_state=reg.try_value("mail_state"),
            mail_zip=reg.try_value("mail_zip"),
        )

    def post(self, request, *args, **kwargs):
        form = FormAB3(request.POST)
        if form.validate():
            step = Step_AB_3(form.data)
            if step.run():
                update_data = form.data
                update_data["validated_addresses"] = step.validated_addresses
                request.registrant.update(update_data)
                request.registrant.addr_lookup_complete = step.addr_lookup_complete

                # override initial county guess with best guess based on validated address
                zip5 = request.registrant.best_zip5()
                county = ZIPCode.guess_county(zip5)
                logger.info("Lookup county %s based on ZIP5 %s" % (county, zip5))
                request.registrant.county = county
                request.registrant.save()

                session_manager = SessionManager(request.registrant, step)
                return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormAB3 failed to validate: {}".format(form.errors))

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
        context["previous_step_url"] = reverse("ksvotes:ab.election_picker")
        return context

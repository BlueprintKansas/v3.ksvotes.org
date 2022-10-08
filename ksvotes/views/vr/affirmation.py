# -*- coding: utf-8 -*-
from ksvotes.forms.vr_7 import FormVR7
from ksvotes.forms.county_picker import CountyPicker
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.steps import Step_VR_7
from ksvotes.services.county_mailer import CountyMailer
from ksvotes.views.step_view import StepView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class VR7View(StepView):
    template_name = "vr/affirmation.html"

    def get_form(self):
        return FormVR7()

    def post(self, request, *args, **kwargs):
        form = FormVR7(request.POST)
        if form.validate():
            step = Step_VR_7(form.data)
            reg = request.registrant
            clerk = reg.try_clerk()

            # if we don't have a VR form to affirm, redirect to Step 0
            if not reg.try_value("vr_form", False):
                return redirect(reverse("ksvotes-i18n:home.index"))

            if step.run():
                reg.update(form.data)
                reg.save()

                mailer = CountyMailer(reg, clerk, "vr_form")
                r = mailer.send()

                # any error gets a special page
                for k in ["clerk", "receipt"]:
                    if k not in r or "MessageId" not in r[k] or not r[k]["MessageId"]:
                        # TODO log New Relic event
                        return render(request, "email_error.html", {"clerk": clerk})

                reg.update({"vr_form_message_id": r["clerk"]["MessageId"]})
                reg.vr_completed_at = timezone.now()
                reg.save()

                session_manager = SessionManager(reg, step)
                return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormVR7 failed to validate: {}".format(form.errors))

        # if anything failed to validate or run, re-render
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs) | {"form": form},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["current_step"] = 7
        context["previous_step_url"] = reverse("ksvotes-i18n:vr.preview")
        context["preview_img"] = self.request.registrant.try_value("vr_form")
        context["clerk"] = self.request.registrant.try_clerk()
        context["county_picker"] = CountyPicker()
        return context

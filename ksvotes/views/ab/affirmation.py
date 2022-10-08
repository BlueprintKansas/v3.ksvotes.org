# -*- coding: utf-8 -*-
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.county_mailer import CountyMailer
from ksvotes.services.id_action_mailer import IdActionMailer
from ksvotes.services.steps import Step_AB_7
from ksvotes.forms.ab_7 import FormAB7
from ksvotes.forms.county_picker import CountyPicker
from ksvotes.views.step_view import StepView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class AB7View(StepView):
    template_name = "ab/affirmation.html"

    def get_form(self):
        return FormAB7()

    def post(self, request, *args, **kwargs):
        form = FormAB7(request.POST)
        if form.validate():
            step = Step_AB_7(form.data)
            reg = request.registrant
            clerk = reg.try_clerk()

            # if we don't have a signed AB form to affirm, redirect
            if not reg.try_value("ab_forms", False):
                if not reg.try_value("signature_string", False):
                    return redirect(reverse("ksvotes-i18n:home.index"))
                else:
                    return redirect(reverse("ksvotes-i18n:ab.preview"))

            if step.run():
                reg.update(form.data)
                reg.save()

                mailer = CountyMailer(reg, clerk, "ab_forms")
                r = mailer.send()

                # if there was no ID string defined, send the action-needed email
                if not reg.ab_permanent and not reg.try_value("ab_identification"):
                    id_action_mailer = IdActionMailer(reg, clerk)
                    resp = id_action_mailer.send()
                    reg.update({"ab_id_action_email_sent": resp["MessageId"]})

                # any error gets a special page
                for k in ["clerk", "receipt"]:
                    if k not in r or "MessageId" not in r[k] or not r[k]["MessageId"]:
                        # TODO log New Relic event
                        return render(request, "email_error.html", {"clerk": clerk})

                reg.update({"ab_forms_message_id": r["clerk"]["MessageId"]})
                reg.ab_completed_at = timezone.now()
                reg.save()

            session_manager = SessionManager(reg, step)
            return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormAB7 failed to validate: {}".format(form.errors))

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
        context["previous_step_url"] = reverse("ksvotes-i18n:ab.preview")
        context["preview_imgs"] = self.request.registrant.try_value("ab_forms")
        context["clerk"] = self.request.registrant.try_clerk()
        context["county_picker"] = CountyPicker()
        return context

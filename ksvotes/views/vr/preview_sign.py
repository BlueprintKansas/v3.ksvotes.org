# -*- coding: utf-8 -*-
from ksvotes.services.nvris_client import NVRISClient
from django.utils import timezone
from ksvotes.forms.vr_6 import FormVR6
from ksvotes.services.session_manager import SessionManager
from ksvotes.services.steps import Step_VR_6
from ksvotes.views.step_view import StepView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class VR6View(StepView):
    template_name = "vr/preview-sign.html"

    def get_form(self):
        reg = self.request.registrant
        return FormVR6(signature_string=reg.try_value("signature_string"))

    def post(self, request, *args, **kwargs):
        # reading entire body, one attempt to workaround gunicorn buffering
        # and possible cause of H18 heroku errors
        raw_body_bytes = request.body
        logger.info("FormVR6 received signature {} bytes".format(len(raw_body_bytes)))
        form = FormVR6(request.POST)
        if form.validate():
            step = Step_VR_6(form.data)
            reg = request.registrant
            if step.run():
                # add signature img but do not save till we have signed form too.
                reg.update(form.data)

                # sign the form and cache the image for next step
                nvris_client = NVRISClient(reg)
                signed_vr_form = nvris_client.get_vr_form()
                if signed_vr_form:
                    reg.update({"vr_form": signed_vr_form})
                    reg.signed_at = timezone.now()
                    reg.save()
                    session_manager = SessionManager(reg, step)
                    return redirect(session_manager.get_redirect_url())

        else:
            logger.debug("FormVR6 failed to validate: {}".format(form.errors))

        # if anything failed to validate or run, re-render
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs) | {"form": form},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["current_step"] = 6
        context["previous_step_url"] = reverse("ksvotes-i18n:vr.identification")
        context["reg"] = self.request.registrant  # TODO need this?
        nvris_client = NVRISClient(self.request.registrant)
        context["preview_img"] = nvris_client.get_vr_form()
        return context

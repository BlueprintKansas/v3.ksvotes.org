# -*- coding: utf-8 -*-
from ksvotes.services.nvris_client import NVRISClient
from ksvotes.forms.county_picker import CountyPicker
from ksvotes.forms.ab_6 import FormAB6
from ksvotes.services.steps import Step_AB_6
from ksvotes.services.session_manager import SessionManager
from ksvotes.views.step_view import StepView
from django.shortcuts import redirect, render
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class AB6View(StepView):
    template_name = "ab/preview-sign.html"

    def get_form(self):
        reg = self.request.registrant
        return FormAB6(signature_string=reg.try_value("signature_string"))

    def post(self, request, *args, **kwargs):
        # reading entire body, one attempt to workaround gunicorn buffering
        # and possible cause of H18 heroku errors
        raw_body_bytes = request.body
        logger.info("FormAB6 received signature {} bytes".format(len(raw_body_bytes)))
        form = FormAB6(request.POST)
        if form.validate():
            step = Step_AB_6(form.data)
            reg = request.registrant
            logger.info(
                "{} starting POST on AB_6 signature preview".format(reg.session_id)
            )

            if step.run():
                # add signature img but do not save till we have signed form too.
                reg.update(form.data)

                # sign the form and cache the image for next step
                logger.info("{} signing AB forms".format(reg.session_id))
                ab_forms = reg.sign_ab_forms()

                if ab_forms and len(ab_forms) > 0:
                    reg.save()
                    session_manager = SessionManager(reg, step)
                    return redirect(session_manager.get_redirect_url())
        else:
            logger.debug("FormAB6 failed to validate: {}".format(form.errors))

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
        context["previous_step_url"] = reverse("ksvotes:ab.identification")

        # always generate a new unsigned form for preview
        preview_imgs = []
        reg = self.request.registrant
        nvris_client = NVRISClient(reg)
        for election in reg.elections():
            logger.info(
                "{} Generating unsigned preview for election {}".format(
                    reg.session_id, election
                )
            )
            preview_img = nvris_client.get_ab_form(election)
            if preview_img:
                preview_imgs.append(preview_img)
        context["preview_imgs"] = preview_imgs
        context["clerk"] = reg.try_clerk()
        context["county_picker"] = CountyPicker()
        context["registrant"] = reg
        return context

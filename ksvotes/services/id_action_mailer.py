# -*- coding: utf-8 -*-
from ksvotes.services.ses_mailer import SESMailer
import os
from django.utils.translation import gettext_lazy as lazy_gettext
from django.template.loader import render_to_string
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class IdActionMailer:
    def __init__(self, registrant, clerk):
        self.ses = SESMailer()
        self.registrant = registrant
        self.clerk = clerk
        if self.clerk == None:
            raise ValueError("No Clerk for County %s" % (registrant.county))
        self.set_subject()
        self.set_body()

    def subject_prefix(self):
        if os.getenv("EMAIL_PREFIX"):
            return os.getenv("EMAIL_PREFIX")
        else:
            return ""

    def set_subject(self):
        self.subject = self.subject_prefix() + lazy_gettext(
            "voter_id_action_email_subject"
        )

    def set_body(self):
        buf = lazy_gettext("voter_id_action_email_intro")
        buf += "\n"
        buf += lazy_gettext("voter_id_action_email_intro2")
        buf += " "
        buf += lazy_gettext("5AB_id_help")
        buf += "\n"
        buf += lazy_gettext("voter_id_action_email_instruction")
        buf += render_to_string("clerk-details.html", {"clerk": self.clerk}).replace(
            "\n", ""
        )
        buf += "\n"
        buf += lazy_gettext("8VR_confirm_5")
        self.body = buf.format(firstname=self.registrant.try_value("name_first"))

    def send(self):
        reg_email = self.registrant.try_value("email")

        message = self.ses.build_msg(
            to=[reg_email], bcc=[], subject=self.subject, body=self.body
        )

        response = self.ses.send_msg(message, settings.EMAIL_FROM)
        logger.info(
            "%s SENT ID Action needed %s" % (self.registrant.session_id, response)
        )

        return response

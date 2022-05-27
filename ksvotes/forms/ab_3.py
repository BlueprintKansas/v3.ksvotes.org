# -*- coding: utf-8 -*-
from wtforms import Form, BooleanField, StringField
from wtforms.validators import DataRequired, Regexp, Optional
from ksvotes.utils import RequiredIfBool
from django.utils.translation import gettext_lazy as lazy_gettext


class FormAB3(Form):
    addr = StringField(
        lazy_gettext("3AB_addr"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
    )
    unit = StringField(lazy_gettext("3_unit"))
    city = StringField(
        lazy_gettext("3_city"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
    )
    state = StringField(
        lazy_gettext("3_state"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
        default="KANSAS",
    )
    zip = StringField(
        lazy_gettext("3_zip"),
        validators=[
            DataRequired(message=lazy_gettext("Required")),
            Regexp(r"^\d{5}(-\d{4})?$", message=lazy_gettext("3_zip_help")),
        ],
    )

    has_mail_addr = BooleanField(lazy_gettext("3_has_mail_addr"))
    mail_addr = StringField(
        lazy_gettext("3AB_mail_addr"),
        validators=[RequiredIfBool("has_mail_addr", message=lazy_gettext("Required"))],
    )
    mail_unit = StringField(lazy_gettext("3_mail_unit"))
    mail_city = StringField(
        lazy_gettext("3_mail_city"),
        validators=[RequiredIfBool("has_mail_addr", message=lazy_gettext("Required"))],
    )
    mail_state = StringField(
        lazy_gettext("3_mail_state"),
        validators=[RequiredIfBool("has_mail_addr", message=lazy_gettext("Required"))],
    )
    mail_zip = StringField(
        lazy_gettext("3_mail_zip"),
        validators=[
            Optional(),
            RequiredIfBool("has_mail_addr", message=lazy_gettext("Required")),
            Regexp(r"^\d{5}$", message=lazy_gettext("3_zip_help")),
        ],
    )

# -*- coding: utf-8 -*-
from wtforms import Form, BooleanField
from wtforms.validators import DataRequired
from django.utils.translation import gettext_lazy as lazy_gettext


class FormVR7(Form):
    affirmation = BooleanField(
        lazy_gettext("7_affirm"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
    )

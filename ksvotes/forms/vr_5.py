# -*- coding: utf-8 -*-
from wtforms import Form, StringField
from wtforms.validators import DataRequired
from django.utils.translation import gettext_lazy as lazy_gettext


class FormVR5(Form):
    identification = StringField(
        lazy_gettext("5VR_id"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
    )

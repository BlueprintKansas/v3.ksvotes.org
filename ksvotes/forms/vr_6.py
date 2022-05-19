# -*- coding: utf-8 -*-
from wtforms import Form, HiddenField
from wtforms.validators import DataRequired, Regexp
from django.utils.translation import gettext_lazy as lazy_gettext


class FormVR6(Form):
    signature_string = HiddenField(
        lazy_gettext("6_sign"),
        validators=[
            DataRequired(message=lazy_gettext("Required")),
            Regexp("^data:image/png;", message="Bad Format"),
        ],
    )

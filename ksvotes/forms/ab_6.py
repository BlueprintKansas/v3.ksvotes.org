# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired, Regexp
from flask_babel import lazy_gettext


class FormAB6(FlaskForm):
    signature_string = HiddenField(
        lazy_gettext("6_sign"),
        validators=[
            DataRequired(message=lazy_gettext("Required")),
            Regexp("^data:image/png;", message="Bad Format"),
        ],
    )

# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext


class FormVR4(FlaskForm):
    party = SelectField(
        lazy_gettext("4_party"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
        choices=[
            ("", ""),
            ("Democratic", "Democratic"),
            ("Republican", "Republican"),
            ("Unaffiliated", "Unaffiliated"),
            ("Libertarian", "Libertarian"),
        ],
    )

# -*- coding: utf-8 -*-
from wtforms import Form, SelectField
from wtforms.validators import DataRequired
from django.utils.translation import gettext_lazy as lazy_gettext
from ksvotes.utils import read_parties


class FormVR4(Form):
    party = SelectField(
        lazy_gettext("4_party"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
        choices=[("", "")] + read_parties("vr-parties.txt"),
    )

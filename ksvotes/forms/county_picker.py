# -*- coding: utf-8 -*-
from wtforms import Form, SelectField
from wtforms.validators import Optional
from ksvotes.utils import construct_county_choices
from django.utils.translation import gettext_lazy as lazy_gettext


class CountyPicker(Form):
    county = SelectField(
        lazy_gettext("0_county"),
        validators=[Optional()],
        choices=construct_county_choices(lazy_gettext("0_county")),
    )

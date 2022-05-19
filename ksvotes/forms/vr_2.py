# -*- coding: utf-8 -*-
from wtforms import Form, BooleanField, StringField, SelectField
from wtforms.validators import DataRequired
from ksvotes.utils import RequiredIfBool
from django.utils.translation import gettext_lazy as lazy_gettext


class FormVR2(Form):
    prefix = SelectField(
        lazy_gettext("2_prefix"),
        choices=[
            ("", lazy_gettext("2_optional_select")),
            ("mr", "Mr."),
            ("mrs", "Mrs."),
            ("miss", "Miss"),
            ("ms", "Ms."),
        ],
    )
    name_first = StringField(
        lazy_gettext("2_first"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
    )
    name_middle = StringField(lazy_gettext("2_middle"))
    name_last = StringField(
        lazy_gettext("2_last"),
        validators=[DataRequired(message=lazy_gettext("Required"))],
    )
    suffix = SelectField(
        lazy_gettext("2_suffix"),
        choices=[
            ("", lazy_gettext("2_optional_select")),
            ("jr", "Jr."),
            ("sr", "Sr."),
            ("ii", "II"),
            ("iii", "III"),
            ("iv", "IV"),
        ],
    )
    has_prev_name = BooleanField(lazy_gettext("2_has_prev_name"))
    prev_prefix = SelectField(
        lazy_gettext("2_prev_prefix"),
        choices=[
            ("", lazy_gettext("2_prev_prefix")),
            ("mr", "Mr."),
            ("mrs", "Mrs."),
            ("miss", "Miss"),
            ("ms", "Ms."),
        ],
    )
    prev_name_first = StringField(
        lazy_gettext("2_prev_first"),
        validators=[RequiredIfBool("has_prev_name", message=lazy_gettext("Required"))],
    )
    prev_name_middle = StringField(lazy_gettext("2_prev_middle"))
    prev_name_last = StringField(
        lazy_gettext("2_prev_last"),
        validators=[RequiredIfBool("has_prev_name", message=lazy_gettext("Required"))],
    )
    prev_suffix = SelectField(
        lazy_gettext("2_prev_suffix"),
        choices=[
            ("", lazy_gettext("2_prev_suffix")),
            ("jr", "Jr."),
            ("sr", "Sr."),
            ("ii", "II"),
            ("iii", "III"),
            ("iv", "IV"),
        ],
    )

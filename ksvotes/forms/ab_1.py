# -*- coding: utf-8 -*-
from wtforms import Form, SelectField, SelectMultipleField, widgets, StringField
from wtforms.validators import DataRequired
from django.utils.translation import gettext_lazy as lazy_gettext
from ksvotes.utils import is_even_year, read_parties
import logging

logger = logging.getLogger(__name__)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

    def pre_validate(self, form):
        # Prevent "not a valid choice" error
        pass

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = "|".join(valuelist)
        else:
            self.data = ""


# based on
# https://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
class RequiredIfFieldContains(DataRequired):
    def __init__(self, other_field_name, value, *args, **kwargs):
        self.other_field_name = other_field_name
        self.value = value
        super(RequiredIfFieldContains, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        other_field_contains = False
        for string in self.value:
            if string in other_field.data:
                other_field_contains = True
        if other_field_contains:
            super(RequiredIfFieldContains, self).__call__(form, field)


class FormAB1(Form):
    elections = MultiCheckboxField(
        lazy_gettext("1AB_select_election"),
        choices=[],  # defer till runtime
        validators=[DataRequired(message=lazy_gettext("Required"))],
    )

    perm_reason = StringField(
        lazy_gettext("1AB_perm_reason"),
        validators=[RequiredIfFieldContains("elections", ["permanent"])],
    )

    party = SelectField(
        lazy_gettext("1AB_party_help"),
        choices=[
            ("", lazy_gettext("1AB_select_party")),
        ]
        + read_parties("ab-parties.txt"),
        default="",
    )

    def validate_party(form, field):
        """Party is only required on primaries in even numbered years"""
        if is_even_year():
            validator = RequiredIfFieldContains("elections", ["Prim"])
            validator(form, field)

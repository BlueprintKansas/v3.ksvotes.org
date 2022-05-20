# -*- coding: utf-8 -*-
from wtforms import Form, RadioField, widgets
from wtforms.widgets import html_params
from wtforms.validators import DataRequired
from markupsafe import Markup
from django.utils.translation import gettext_lazy as lazy_gettext
from ksvotes.utils import str_to_bool

import logging

logger = logging.getLogger(__name__)


class InlineListWidget(widgets.ListWidget):
    def __call__(self, field, **kwargs):
        self.html_tag = "div"
        kwargs.setdefault("id", field.id)
        html = ["<%s %s>" % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(
                    "<div class='form-check form-check-inline'>%s %s</div>"
                    % (subfield.label, subfield(aria_labelledby=field.id))
                )
            else:
                html.append(
                    "<div class='form-check form-check-inline'>%s %s</div>"
                    % (subfield(aria_labelledby=field.id), subfield.label)
                )
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))


class RadioBooleanField(RadioField):
    widget = InlineListWidget()
    option_widget = widgets.RadioInput()


class FormVR1(Form):
    is_citizen = RadioBooleanField(
        lazy_gettext("1VR_citizen"),
        choices=[
            (True, lazy_gettext("choice_yes")),
            (False, lazy_gettext("choice_no")),
        ],
        default="False",  # always require user action, string not boolean.
        validators=[DataRequired(message=lazy_gettext("Required"))],
        coerce=str_to_bool,
    )
    is_eighteen = RadioBooleanField(
        lazy_gettext("1VR_18"),
        choices=[
            (True, lazy_gettext("choice_yes")),
            (False, lazy_gettext("choice_no")),
        ],
        validate_choice=False,  # TODO is this optimal for optional value?
        coerce=str_to_bool,
    )

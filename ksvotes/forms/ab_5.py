# -*- coding: utf-8 -*-
from wtforms import Form, StringField
from wtforms.validators import Optional, Regexp
from ksvotes.utils import KS_DL_PATTERN
from django.utils.translation import gettext_lazy as lazy_gettext


class KSIDField(StringField):
    def process_formdata(self, valuelist):
        dl = valuelist[0].replace("-", "").replace("/", "")
        if len(dl) == 9:
            dl = "-".join((dl[:3], dl[3:5], dl[5:]))
        self.data = dl


class FormAB5(Form):
    ab_identification = KSIDField(
        lazy_gettext("5AB_id"),
        validators=[
            Optional(),
            Regexp(KS_DL_PATTERN, message=lazy_gettext("5AB_id_pattern")),
        ],
    )

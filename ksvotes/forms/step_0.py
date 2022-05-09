from wtforms import Form, StringField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, Regexp, Optional
from wtforms.fields import EmailField, TelField
from dateutil.relativedelta import relativedelta
from django.utils.translation import gettext_lazy as lazy_gettext
import datetime
import os
import re

class DOBField(StringField):
    def process_formdata(self, valuelist):
        if valuelist is None or len(valuelist) == 0:
            return False
        mdy = re.search(r"^(\d{2})(\d{2})(\d{4})$", re.sub(r"\D", '', valuelist[0]))
        if not mdy:
            return False
        self.data = '{m}/{d}/{y}'.format(m=mdy.group(1), d=mdy.group(2), y=mdy.group(3))

class FormStep0(Form):
    ref = HiddenField()
    name_first = StringField(lazy_gettext(u'0_first'), validators=[DataRequired(message=lazy_gettext(u'Required'))])
    name_last = StringField(lazy_gettext(u'0_last'), validators=[DataRequired(message=lazy_gettext(u'Required'))])
    dob = DOBField(
        lazy_gettext(u'0_dob'),
        validators=[
            DataRequired(message=lazy_gettext(u'Required')),
            Regexp(r"^\d{2}[\/\-]?\d{2}[\/\-]?\d{4}$", message=lazy_gettext(u'0_dob_flag'))
        ]
    )

    zip = StringField(lazy_gettext(u'3_zip'),
        validators=[
            DataRequired(message=lazy_gettext(u'Required')),
            Regexp(r"^\d{5}(-\d{4})?$", message=lazy_gettext(u'3_zip_help'))
        ]
    )

    email = EmailField(lazy_gettext(u'0_email'),
        validators=[DataRequired(message=lazy_gettext(u'Required')),
        Email(message=lazy_gettext(u'0_email_flag'))]
    )
    phone = TelField(lazy_gettext(u'0_phone'),
        validators=[Optional(), Regexp(r"^\d{3}[\-\.]?\d{3}[\-\.]?\d{4}$", message=lazy_gettext(u'0_phone_help'))]
    )

    if os.getenv('RECAPTCHA_KEY'):
        # TODO currently un-used -- do we need to support going forward?
        recaptcha = RecaptchaField()

    def validate_dob(self, field):
        time_now = datetime.datetime.utcnow()
        dob = re.sub(r"\D", '', field.data)
        mdy = re.search(r"^(\d{2})(\d{2})(\d{4})$", dob)
        if not mdy:
            field.errors.append(lazy_gettext(u'0_dob_help'))
            return False
        time_dob = datetime.datetime.strptime(dob, '%m%d%Y')
        diff = relativedelta(time_now, time_dob).years
        if diff <= 15:
            field.errors.append(lazy_gettext(u'0_dob_help'))
            return False
        return True

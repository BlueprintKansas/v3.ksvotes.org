from django import template
from django.utils.translation import gettext_lazy as _
import logging

register = template.Library()
logger = logging.getLogger(__name__)

@register.inclusion_tag("wtf/text.html")
def zipcode_field(field, required=False):
    html_attrs = {
        "class": "form-control",
        'pattern': '\d{5}.*',
        'autocomplete':'off',
        'data-parsley-trigger':'focusout',
        'data-parsley-pattern-message': _('3_zip_help'),
        'data-parsley-pattern': "/^\d{5}([\-]\d{4})?$/",
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _('Required')
    return {
        "help_text": _('3_zip_help'),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }

@register.inclusion_tag("wtf/text.html")
def text_field(field, help_text_key, required=False):
    html_attrs = {
        "class": "form-control",
        'autocomplete':'off',
        'data-parsley-trigger':'focusout'
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _('Required')
    return {
        "help_text": _(help_text_key),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }

@register.inclusion_tag("wtf/text.html")
def dob_field(field, required=False):
    html_attrs = {
        "class": "form-control",
        'autocomplete':'off',
        'data-parsley-trigger':'focusout',
        'data-parsley-pattern-message': _('0_dob_flag'),
        'data-parsley-pattern': "/^\d{2}[\/-]?\d{2}[\/\-]?\d{4}$/",
        'data-parsley-dob-limit':"true",
        'data-parsley-dob-limit-message': _('0_dob_flag'),
        'placeholder':'mm/dd/yyyy',
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _('Required')
    return {
        "help_text": _("0_dob_help"),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }

@register.inclusion_tag("wtf/text.html")
def email_field(field, required=False):
    html_attrs = {
        "class": "form-control",
        'data-parsley-trigger': 'focusout',
        'data-parsley-type': 'email',
        'data-parsley-type-message': _('0_email_flag'),
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _('Required')
    return {
        "help_text": _("0_email_help"),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }

@register.inclusion_tag("wtf/text.html")
def phone_field(field, required=False):
    html_attrs = {
        "class": "form-control",
        'data-parsley-trigger': 'focusout',
        'data-parsley-pattern': '/^\d{3}[\-\.]?\d{3}[\-\.]?\d{4}$/',
        'data-parsley-pattern-message': _('0_phone_flag'),
        'data-parsley-phone-limit':"true",
        'data-parsley-phone-limit-message': _('0_phone_flag'),
        'placeholder': 'xxx-xxx-xxxx',
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _('Required')
    return {
        "help_text": _("0_phone_help"),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }

# -*- coding: utf-8 -*-
from django import template
from django.utils.translation import gettext_lazy as _
import logging

register = template.Library()
logger = logging.getLogger(__name__)


@register.inclusion_tag("wtf/text.html")
def zipcode_field(field, required=False):
    html_attrs = {
        "class": "form-control",
        "pattern": r"\d{5}(-\d{4})?",
        "autocomplete": "off",
        "data-parsley-trigger": "focusout",
        "data-parsley-pattern-message": _("3_zip_help"),
        "data-parsley-pattern": r"/^\d{5}([\-]\d{4})?$/",
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
    return {
        "help_text": _("3_zip_help"),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }


@register.inclusion_tag("wtf/text.html")
def hidden_field(field):
    html_attrs = {
        "class": "form-hidden",
    }
    return {
        "html": field(**html_attrs),
        "errors": None,
        "help_text": None,
        "label": "",
    }


@register.inclusion_tag("wtf/text.html")
def text_field(field, help_text_key=None, required=False):
    html_attrs = {
        "class": "form-control",
        "autocomplete": "off",
        "data-parsley-trigger": "focusout",
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
    return {
        "help_text": (_(help_text_key) if help_text_key else None),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }


@register.inclusion_tag("wtf/text.html")
def readonly_field(field, help_text_key=None, required=False):
    html_attrs = {
        "class": "form-control",
        "autocomplete": "off",
        "data-parsley-trigger": "focusout",
        "disabled": "disabled",
        "readonly": "readonly",
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
    return {
        "help_text": (_(help_text_key) if help_text_key else None),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }


@register.inclusion_tag("wtf/text.html")
def dob_field(field, required=False):
    html_attrs = {
        "class": "form-control",
        "autocomplete": "off",
        "data-parsley-trigger": "focusout",
        "data-parsley-pattern-message": _("0_dob_flag"),
        "data-parsley-pattern": r"/^\d{2}[\/-]?\d{2}[\/\-]?\d{4}$/",
        "data-parsley-dob-limit": "true",
        "data-parsley-dob-limit-message": _("0_dob_flag"),
        "placeholder": "mm/dd/yyyy",
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
    return {
        "help_text": _("0_dob_help"),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }


@register.inclusion_tag("wtf/text.html")
def ks_id_field(field, required=False):
    html_attrs = {
        "class": "form-control",
        "autocomplete": "off",
        "data-parsley-trigger": "focusout",
        "data-parsley-id-pattern": "true",
        "data-parsley-id-pattern-message": _("5AB_id_pattern"),
        "placeholder": "Knn-nn-nnnn",
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
    return {
        "help_text": _("5AB_id_shorthelp"),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }


@register.inclusion_tag("wtf/text.html")
def email_field(field, required=False):
    html_attrs = {
        "class": "form-control",
        "data-parsley-trigger": "focusout",
        "data-parsley-type": "email",
        "data-parsley-type-message": _("0_email_flag"),
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
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
        "data-parsley-trigger": "focusout",
        "data-parsley-pattern": r"/^\d{3}[\-\.]?\d{3}[\-\.]?\d{4}$/",
        "data-parsley-pattern-message": _("0_phone_flag"),
        "data-parsley-phone-limit": "true",
        "data-parsley-phone-limit-message": _("0_phone_flag"),
        "placeholder": "xxx-xxx-xxxx",
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
    return {
        "help_text": _("0_phone_help"),
        "label": field.label,
        "html": field(**html_attrs),
        "errors": field.errors,
    }


@register.inclusion_tag("wtf/boolean.html")
def boolean_field(field, help_text, required=False):
    html_attrs = {}
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
    label_attrs = {"class": "pr-3"}
    return {
        "label": field.label(**label_attrs),
        "help_text": help_text,
        "html": field(**html_attrs),
        "errors": field.errors,
    }


@register.inclusion_tag("wtf/checkbox.html")
def checkbox_field(field, help_text, required=False):
    html_attrs = {
        "class": "form-check-input",
    }
    if required:
        html_attrs["required"] = "required"
        html_attrs["data-parsley-required-message"] = _("Required")
    label_attrs = {"class": "form-check-label pr-3"}
    return {
        "label": field.label(**label_attrs),
        "help_text": help_text,
        "html": field(**html_attrs),
        "errors": field.errors,
    }


@register.inclusion_tag("wtf/multicheckbox.html")
def multicheckbox_field(field, help_text, required=False):
    label_attrs = {"class": "fs-16"}
    return {
        "id": field.id,
        "label": field.label(**label_attrs),
        "required": required,
        "field": field,
        "help_text": help_text,
        "errors": field.errors,
    }

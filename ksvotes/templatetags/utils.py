# -*- coding: utf-8 -*-
from django.template.defaulttags import register
import json


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item_default(dictionary, key, default=""):
    return dictionary.get(key, default)


@register.filter
def tojson(value):
    return json.dumps(value, indent=4, sort_keys=True, default=str)

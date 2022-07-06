# -*- coding: utf-8 -*-
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator


@method_decorator(never_cache, name="dispatch")
class StepView(TemplateView):
    pass

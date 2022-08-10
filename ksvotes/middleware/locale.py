# -*- coding: utf-8 -*-
from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware
import logging

logger = logging.getLogger(__name__)


class LocaleMiddleware(DjangoLocaleMiddleware):
    def process_response(self, request, response):
        if request.method == "POST":
            # do not redirect to the "/en/" locale path if this is a POST,
            # mostly for the existing /ref URLs in the wild.
            return response

        return super().process_response(request, response)

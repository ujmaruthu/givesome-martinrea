# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.http import HttpRequest

from shuup.core.basket.objects import BaseBasket


class BaseBasketCommandMiddleware:
    """
    A basket command middleware to pre-process the kwargs and post-process the response.
    """

    def preprocess_kwargs(self, basket: BaseBasket, request: HttpRequest, command: str, kwargs: dict) -> dict:
        """
        Mutate the `kwargs` that will be passed to the `handler`.
        It is possible to raise a `ValidationError` exception if required.
        """
        return kwargs

    def postprocess_response(
        self, basket: BaseBasket, request: HttpRequest, command: str, kwargs: dict, response: dict
    ) -> dict:
        """
        Mutate the `response` before it is returned by the command dispatcher.
        """
        return response

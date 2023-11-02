# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.views.generic import TemplateView, View

from shuup.core.basket.objects import BasketValidationError
from shuup.front.basket import get_basket_command_dispatcher, get_basket_view


class DefaultBasketView(TemplateView):
    template_name = "shuup/front/basket/default_basket.jinja"

    def get_context_data(self, **kwargs):
        context = super(DefaultBasketView, self).get_context_data()
        basket = self.request.basket
        context["basket"] = basket

        blocking_errors = []
        non_blocking_errors = []

        for validation_error in basket.get_validation_errors():
            if isinstance(validation_error, BasketValidationError):
                if validation_error.blocks_checkout:
                    blocking_errors.append(validation_error)
                else:
                    non_blocking_errors.append(validation_error)
            else:
                blocking_errors.append(validation_error)

        context["errors"] = blocking_errors
        context["warnings"] = non_blocking_errors
        return context


class BasketView(View):
    def dispatch(self, request, *args, **kwargs):
        command = request.POST.get("command")
        if command:
            return get_basket_command_dispatcher(request).handle(command)
        else:
            return get_basket_view()(request, *args, **kwargs)

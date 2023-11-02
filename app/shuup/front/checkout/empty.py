# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView

from shuup.front.checkout import CheckoutPhaseViewMixin


class EmptyPhase(CheckoutPhaseViewMixin, TemplateView):
    identifier = "empty"
    title = _("Empty Basket")

    template_name = "shuup/front/checkout/empty.jinja"

    def process(self):
        pass

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

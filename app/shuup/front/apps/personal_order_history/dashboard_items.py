# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.core.models import Order
from shuup.front.utils.dashboard import DashboardItem


class OrderHistoryItem(DashboardItem):
    title = _("Order history")
    template_name = "shuup/personal_order_history/dashboard.jinja"
    icon = "fa fa-sticky-note-o"
    view_text = _("Show all")

    _url = "shuup:personal-orders"

    def get_context(self):
        context = super(OrderHistoryItem, self).get_context()
        context["orders"] = Order.objects.filter(customer=self.request.customer).order_by("-created_on")[:5]
        return context

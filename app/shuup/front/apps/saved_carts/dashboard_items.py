# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.front.models import StoredBasket
from shuup.front.utils.dashboard import DashboardItem


class SavedCartsItem(DashboardItem):
    template_name = "shuup/saved_carts/dashboard_item.jinja"
    title = _("Saved Carts")
    icon = "fa fa-shopping-cart"
    _url = "shuup:saved_cart.list"

    def get_context(self):
        context = super(SavedCartsItem, self).get_context()
        context["carts"] = StoredBasket.objects.filter(
            persistent=True, deleted=False, customer=self.request.customer, shop=self.request.shop
        )
        return context

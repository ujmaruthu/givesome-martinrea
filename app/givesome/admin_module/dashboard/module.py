# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.utils.translation import ugettext_lazy as _
from shuup.admin.base import AdminModule
from shuup.admin.currencybound import CurrencyBound
from shuup.admin.utils.urls import admin_url


class GivesomeDashboardModule(CurrencyBound, AdminModule):
    name = _("Givesome Vendor Dashboard")

    def get_urls(self):
        return [
            admin_url(
                r"^multivendor/dashboard/$",
                "givesome.admin_module.dashboard.views.GivesomeSupplierDashboardView",
                name="shuup_multivendor.dashboard.supplier",
            )
        ]

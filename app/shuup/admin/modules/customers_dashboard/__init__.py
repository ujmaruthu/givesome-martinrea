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

from .dashboard import get_active_customers_block


class CustomersDashboardModule(AdminModule):
    name = _("Customers Dashboard")

    def get_dashboard_blocks(self, request):
        yield get_active_customers_block(request)

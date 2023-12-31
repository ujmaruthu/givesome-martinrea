# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.admin.dashboard import DashboardNumberBlock
from shuup.core.models import Order


def get_active_customers_block(request):
    shop = request.shop
    customer_ids = set(Order.objects.filter(shop=shop).since(30).values_list("customer_id", flat=True))

    return DashboardNumberBlock(
        id="active_customers_count",
        color="blue",
        title=_("Active customers"),
        value=len(customer_ids),
        icon="fa fa-history",
        subtitle=_("Based on orders within 30 days"),
    )

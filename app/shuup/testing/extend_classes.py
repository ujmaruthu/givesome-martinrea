# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.core.models import ProductMode
from shuup.front.forms.order_forms import ProductOrderForm


class DifferentProductOrderForm(ProductOrderForm):
    template_name = "shuup_testing/different_order_form.jinja"

    def is_compatible(self):
        return self.product.mode == ProductMode.SUBSCRIPTION

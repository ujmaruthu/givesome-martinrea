# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from ._delete import PaymentMethodDeleteView, ShippingMethodDeleteView
from ._edit import PaymentMethodEditView, ShippingMethodEditView
from ._list import PaymentMethodListView, ShippingMethodListView

__all__ = [
    "PaymentMethodDeleteView",
    "PaymentMethodEditView",
    "PaymentMethodListView",
    "ShippingMethodDeleteView",
    "ShippingMethodEditView",
    "ShippingMethodListView",
]

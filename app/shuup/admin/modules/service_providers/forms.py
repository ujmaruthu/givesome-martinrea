# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from shuup.admin.forms import ShuupAdminForm
from shuup.core.models import CustomCarrier, CustomPaymentProcessor


class CustomCarrierForm(ShuupAdminForm):
    class Meta:
        model = CustomCarrier
        exclude = ("identifier",)


class CustomPaymentProcessorForm(ShuupAdminForm):
    class Meta:
        model = CustomPaymentProcessor
        exclude = ("identifier",)

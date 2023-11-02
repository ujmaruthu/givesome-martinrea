# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shuup.core.fields import MoneyValueField
from shuup.core.models import ShuupModel
from shuup.utils.properties import TaxlessPriceProperty


class DonationExtra(ShuupModel):
    order = models.OneToOneField("shuup.Order", related_name="donation_extra", on_delete=models.CASCADE)
    local_currency_total = TaxlessPriceProperty("local_currency_total_value", "currency")
    local_currency_total_value = MoneyValueField(editable=False, verbose_name=_("local currency total"), default=0)

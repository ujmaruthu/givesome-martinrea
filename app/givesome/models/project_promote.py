# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db import models
from shuup.core.models import ShuupModel


class GivesomePromotedProduct(ShuupModel):
    supplier = models.ForeignKey(
        "shuup.Supplier", related_name="promoted_projects", on_delete=models.CASCADE, null=True, blank=True
    )
    office = models.ForeignKey(
        "givesome.GivesomeOffice", related_name="promoted_projects", on_delete=models.CASCADE, null=True, blank=True
    )
    shop_product = models.ForeignKey("shuup.ShopProduct", related_name="promotions", on_delete=models.CASCADE)
    ordering = models.IntegerField(default=0)

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db import models


class ShopProductCatalogDiscountsLink(models.Model):
    """
    Model to store the link between a ShopProduct and Discounts.

    Every time a discount is changed, the linked shop products
    must be reindexed.
    """

    shop_product = models.OneToOneField("shuup.ShopProduct", related_name="discounts_link", on_delete=models.CASCADE)
    discounts = models.ManyToManyField("discounts.Discount", related_name="shop_products_link", blank=True)

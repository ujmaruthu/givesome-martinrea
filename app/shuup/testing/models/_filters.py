# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db import models

from shuup.campaigns.models import CatalogFilter
from shuup.core.models import Category, Contact, Product, ProductType, ShopProduct


class UltraFilter(CatalogFilter):
    model = Category
    identifier = "ufilter2"
    name = "ufilter2"
    products = models.ManyToManyField(Product, related_name="ultrafilter1")
    categories = models.ManyToManyField(Category, related_name="ultrafilter2")
    product_types = models.ManyToManyField(ProductType, related_name="ultrafilter3")
    shop_products = models.ManyToManyField(ShopProduct, related_name="ultrafilter4")

    product = models.ForeignKey(on_delete=models.CASCADE, to=Product, null=True)
    category = models.ForeignKey(on_delete=models.CASCADE, to=Category, null=True, related_name="ultrafilte5")
    product_type = models.ForeignKey(on_delete=models.CASCADE, to=ProductType, null=True)
    derp = models.ForeignKey(on_delete=models.CASCADE, to=Category, null=True, related_name="ultrafilte55")
    contact = models.ForeignKey(on_delete=models.CASCADE, to=Contact, null=True)
    shop_product = models.ForeignKey(on_delete=models.CASCADE, to=ShopProduct, null=True)

# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db import models

from shuup.core.models import ShopProduct


class CatalogFilterCachedShopProduct(models.Model):
    filter = models.ForeignKey(
        on_delete=models.CASCADE, to="CatalogFilter", related_name="cached_shop_products", db_index=True
    )
    shop_product = models.ForeignKey(
        on_delete=models.CASCADE, to=ShopProduct, related_name="cached_catalog_campaign_filters", db_index=True
    )

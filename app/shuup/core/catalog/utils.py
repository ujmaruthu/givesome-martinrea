# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import logging

from shuup import configuration
from shuup.core.catalog import ProductCatalog
from shuup.core.models import ProductMode, ShopProduct

LOGGER = logging.getLogger(__name__)


def reindex_all_shop_products():
    for shop_product in ShopProduct.objects.exclude(product__mode=ProductMode.VARIATION_CHILD):
        try:
            ProductCatalog.index_shop_product(shop_product)

        # try to catch any excetpion here as this might raise anything
        # and we don't want to not reindex products in case of an error
        except Exception:
            LOGGER.exception("Failed to index shop product")

    configuration.set(None, "product_catalog_needs_reindex", False)

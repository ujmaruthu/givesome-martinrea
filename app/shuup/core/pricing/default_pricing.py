# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from typing import Optional, Union

from shuup.core.models import ProductCatalogPrice, ProductCatalogPriceRule, ProductVisibility, ShopProduct
from shuup.core.pricing import PriceInfo, PricingModule


class DefaultPricingModule(PricingModule):
    identifier = "default_pricing"
    name = _("Default Pricing")

    def get_price_info(self, context, product, quantity=1):
        """
        Return a `PriceInfo` calculated from `ShopProduct.default_price`

        Since `ShopProduct.default_price` can be `None` it will
        be set to zero (0) if `None`.
        """
        shop = context.shop
        shop_product = ShopProduct.objects.get(product=product, shop=shop)

        default_price = shop_product.default_price_value or 0

        return PriceInfo(
            price=shop.create_price(default_price * quantity),
            base_price=shop.create_price(default_price * quantity),
            quantity=quantity,
        )

    def _is_shop_product_visible(self, shop_product: "ShopProduct", contact_group_id: Optional[int] = None):
        if next(shop_product.get_visibility_errors(), None):
            return False

        # product is visible to groups only, so only generate prices for them
        if contact_group_id and shop_product.visibility_limit == ProductVisibility.VISIBLE_TO_GROUPS:
            if not shop_product.visibility_groups.filter(pk=contact_group_id).exists():
                return False

        return True

    def index_shop_product(self, shop_product: Union["ShopProduct", int], **kwargs):
        if isinstance(shop_product, int):
            shop_product = ShopProduct.objects.select_related("shop", "product").get(pk=shop_product)

        is_variation_parent = shop_product.product.is_variation_parent()
        visible_groups_ids = []

        # clean up all prices for this product and shop
        ProductCatalogPrice.objects.filter(product_id=shop_product.product_id, shop_id=shop_product.shop_id).delete()

        only_for_authenticated_user = None
        if shop_product.visibility_limit == ProductVisibility.VISIBLE_TO_LOGGED_IN:
            only_for_authenticated_user = True

        # product is visible to groups only, so only generate prices for them
        if shop_product.visibility_limit == ProductVisibility.VISIBLE_TO_GROUPS:
            visible_groups_ids = list(shop_product.visibility_groups.values_list("pk", flat=True))
        else:
            # when prices can be available to any group, make sure to
            # index prices to any group as well, this is what None means
            visible_groups_ids.append(None)

        # this group is a default group, remove it from there
        for supplier_id in shop_product.suppliers.values_list("pk", flat=True):
            for group_id in visible_groups_ids:
                catalog_rule = ProductCatalogPriceRule.objects.get_or_create(
                    module_identifier=self.identifier,
                    contact_group_id=group_id,
                    contact=None,
                    authenticated_user=only_for_authenticated_user,
                )[0]

                ProductCatalogPrice.objects.update_or_create(
                    product_id=shop_product.product_id,
                    shop_id=shop_product.shop_id,
                    supplier_id=supplier_id,
                    catalog_rule=catalog_rule,
                    defaults=dict(
                        is_visible=self._is_shop_product_visible(shop_product),
                        price_value=shop_product.default_price_value or Decimal(),
                    ),
                )

        # index the price of all children shop products
        if is_variation_parent:
            children_shop_product = ShopProduct.objects.select_related("product", "shop").filter(
                shop=shop_product.shop, product__variation_parent_id=shop_product.product_id
            )
            for child_shop_product in children_shop_product:
                self.index_shop_product(child_shop_product)

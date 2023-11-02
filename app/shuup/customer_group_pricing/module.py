# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from decimal import Decimal
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from typing import Optional, Union

from shuup.core.models import (
    ProductCatalogDiscountedPrice,
    ProductCatalogDiscountedPriceRule,
    ProductCatalogPrice,
    ProductCatalogPriceRule,
    ProductVisibility,
    ShopProduct,
)
from shuup.core.pricing import DiscountModule, PriceInfo, PricingModule

from .models import CgpDiscount, CgpPrice


class CustomerGroupPricingModule(PricingModule):
    identifier = "customer_group_pricing"
    name = _("Customer Group Pricing")

    def get_price_info(self, context, product, quantity=1):
        shop = context.shop
        product_id = product if isinstance(product, int) else product.pk
        shop_product = ShopProduct.objects.filter(product_id=product_id, shop=shop).only("default_price_value").first()

        if not shop_product:
            return PriceInfo(price=shop.create_price(0), base_price=shop.create_price(0), quantity=quantity)

        default_price = shop_product.default_price_value or 0
        filter = Q(product_id=product_id, shop=shop, price_value__gt=0, group__in=context.customer.groups.all())
        result = CgpPrice.objects.filter(filter).order_by("price_value")[:1].values_list("price_value", flat=True)

        if result:
            price = result[0]
            if default_price > 0:
                price = min([default_price, price])
        else:
            price = default_price

        return PriceInfo(
            price=shop.create_price(price * quantity),
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

        customer_group_prices = dict(
            CgpPrice.objects.filter(product_id=shop_product.product_id, shop_id=shop_product.shop_id).values_list(
                "group_id", "price_value"
            )
        )

        # product is visible to groups only, so only generate prices for them
        if shop_product.visibility_limit == ProductVisibility.VISIBLE_TO_GROUPS:
            visible_groups_ids = list(shop_product.visibility_groups.values_list("pk", flat=True))
        else:
            # when prices can be available to any group, make sure to
            # index prices to any group as well, this is what None means
            visible_groups_ids.append(None)

            # extend the groups with the groups that have prices configured
            if customer_group_prices:
                visible_groups_ids.extend(customer_group_prices.keys())

        # this group is a default group, remove it from there
        for supplier_id in shop_product.suppliers.values_list("pk", flat=True):
            for group_id in visible_groups_ids:
                catalog_rule = ProductCatalogPriceRule.objects.get_or_create(
                    module_identifier=self.identifier,
                    contact_group_id=group_id,
                    contact=None,
                    authenticated_user=only_for_authenticated_user,
                )[0]

                price = customer_group_prices.get(group_id, shop_product.default_price_value)

                ProductCatalogPrice.objects.update_or_create(
                    product_id=shop_product.product_id,
                    shop_id=shop_product.shop_id,
                    supplier_id=supplier_id,
                    catalog_rule=catalog_rule,
                    defaults=dict(
                        is_visible=self._is_shop_product_visible(shop_product),
                        price_value=price or Decimal(),
                    ),
                )

        # index the price of all children shop products
        if is_variation_parent:
            children_shop_product = ShopProduct.objects.select_related("product", "shop").filter(
                shop=shop_product.shop, product__variation_parent_id=shop_product.product_id
            )
            for child_shop_product in children_shop_product:
                self.index_shop_product(child_shop_product)


class CustomerGroupDiscountModule(DiscountModule):
    identifier = "customer_group_discount"
    name = _("Customer Group Discount")

    def discount_price(self, context, product, price_info):
        """
        Get the best discount amount for context.
        """
        shop = context.shop
        product_id = product if isinstance(product, int) else product.pk

        cgp_discount = (
            CgpDiscount.objects.filter(
                shop_id=shop.id,
                product_id=product_id,
                group__in=context.customer.groups.all(),
                discount_amount_value__gt=0,
            )
            .order_by("-discount_amount_value")
            .first()
        )

        if cgp_discount:
            total_discount = cgp_discount.discount_amount * price_info.quantity
            # do not allow the discount to be greater than the price
            return PriceInfo(
                price=max(price_info.price - total_discount, context.shop.create_price(0)),
                base_price=price_info.base_price,
                quantity=price_info.quantity,
                expires_on=price_info.expires_on,
            )

        return price_info

    def index_shop_product(self, shop_product: Union["ShopProduct", int], **kwargs):
        """
        Index the shop product discounts
        """
        if isinstance(shop_product, int):
            shop_product = ShopProduct.objects.select_related("shop", "product").get(pk=shop_product)

        is_variation_parent = shop_product.product.is_variation_parent()

        # index the discounted price of all children shop products
        if is_variation_parent:
            children_shop_product = ShopProduct.objects.select_related("product", "shop").filter(
                shop=shop_product.shop, product__variation_parent=shop_product.product
            )
            for child_shop_product in children_shop_product:
                self.index_shop_product(child_shop_product)

        # clear all existing discounted prices for this discount module
        ProductCatalogDiscountedPrice.objects.filter(
            catalog_rule__module_identifier=self.identifier,
            product_id=shop_product.product_id,
            shop_id=shop_product.shop_id,
        ).delete()

        only_for_authenticated_user = shop_product.visibility_limit == ProductVisibility.VISIBLE_TO_LOGGED_IN

        # index all the discounted prices
        for customer_group_discount in CgpDiscount.objects.filter(
            product_id=shop_product.product_id, shop_id=shop_product.shop_id
        ):
            catalog_rule = ProductCatalogDiscountedPriceRule.objects.get_or_create(
                module_identifier=self.identifier,
                contact_group=customer_group_discount.group,
                contact=None,
                valid_start_date=None,
                valid_end_date=None,
                valid_start_hour=None,
                valid_end_hour=None,
                valid_weekday=None,
            )[0]

            for supplier_id in shop_product.suppliers.values_list("pk", flat=True):
                # get the indexed product calculated from the pricing module
                catalog_price = (
                    ProductCatalogPrice.objects.only("price_value")
                    .filter(
                        Q(
                            product_id=shop_product.product_id,
                            shop_id=shop_product.shop_id,
                            supplier_id=supplier_id,
                            catalog_rule__contact=None,
                        ),
                        Q(
                            Q(catalog_rule__authenticated_user=only_for_authenticated_user)
                            | Q(catalog_rule__authenticated_user__isnull=True)
                        ),
                        Q(
                            Q(catalog_rule__contact_group_id=customer_group_discount.group_id)
                            | Q(catalog_rule__contact_group__isnull=True)
                        ),
                    )
                    .order_by("price_value")
                    .first()
                )

                if catalog_price:
                    normal_price = catalog_price.price_value
                else:
                    normal_price = shop_product.default_price_value or Decimal()

                # there is no valid price
                if not normal_price:
                    return

                # the discount is always over the default product price
                discounted_price = max(normal_price - customer_group_discount.discount_amount_value, Decimal())

                ProductCatalogDiscountedPrice.objects.update_or_create(
                    product_id=shop_product.product_id,
                    shop_id=shop_product.shop_id,
                    supplier_id=supplier_id,
                    catalog_rule=catalog_rule,
                    defaults=dict(discounted_price_value=discounted_price),
                )

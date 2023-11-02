# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db.models import OuterRef, Q, Subquery
from django.db.models.query import QuerySet
from django.utils import timezone
from typing import Optional, Union

from shuup.core.catalog.signals import index_catalog_shop_product
from shuup.core.models import (
    AnonymousContact,
    Contact,
    Product,
    ProductCatalogDiscountedPrice,
    ProductCatalogDiscountedPriceRule,
    ProductCatalogPrice,
    ProductCatalogPriceRule,
    Shop,
    ShopProduct,
    ShopProductVisibility,
    Supplier,
)
from shuup.core.pricing import get_discount_modules, get_pricing_module
from shuup.core.utils.users import is_user_all_seeing


class ProductCatalogContext:
    """
    The catalog context object helps the catalog object
    to filter products according to the context's attributes.

    `shop` can be either a Shop instance or a shop id,
        used to filter the products for the given shop.

    `supplier` can be either a Supplier instance or a supplier id,
        used to filter the products for the given supplier.

    `user` can be either a User instance or a user id,
        used to filter the products for the given user.

    `contact` a Contact instance used to filter the products for the given contact.

    `purchasable_only` filter the products that can be purchased.
    """

    def __init__(
        self,
        shop: Optional[Union[Shop, int]] = None,
        supplier: Optional[Union[Supplier, int]] = None,
        user: Optional[Union[AbstractUser, AnonymousUser, int]] = None,
        contact: Optional[Contact] = None,
        purchasable_only: bool = True,
    ):
        self.shop = shop
        self.supplier = supplier
        self.user = user
        self.contact = contact
        self.purchasable_only = purchasable_only


def get_price_contact_filter(contact: Optional[Contact]):
    if contact:
        # filter all prices for the contact OR to the groups of the contact

        # evaluate contact group to prevent doing expensive joins on db
        contact_groups_ids = list(contact.groups.values_list("pk", flat=True))
        filters = Q(
            Q(
                Q(contact=contact)
                | Q(contact_group_id__in=contact_groups_ids)
                | Q(contact_group__isnull=True, contact__isnull=True)
            ),
        )

        # the contact has a user attached
        if getattr(contact, "user", None):
            filters &= Q(Q(authenticated_user=True) | Q(authenticated_user__isnull=True))
        else:
            filters &= Q(Q(authenticated_user=False) | Q(authenticated_user__isnull=True))

        return filters

    # no contact
    return Q(
        Q(
            Q(contact_group__isnull=True, contact__isnull=True)
            | Q(contact_group_id=AnonymousContact.get_default_group().pk),
        ),
        Q(Q(authenticated_user=False) | Q(authenticated_user__isnull=True)),
    )


def get_discounted_price_contact_filter(contact: Optional[Contact]):
    if contact:
        # filter all prices for the contact OR to the groups of the contact
        # evaluate contact group to prevent doing expensive joins on db
        contact_groups_ids = list(contact.groups.values_list("pk", flat=True))
        return Q(
            Q(
                Q(contact=contact)
                | Q(contact_group_id__in=contact_groups_ids)
                | Q(contact_group__isnull=True, contact__isnull=True)
            ),
        )
    # anonymous contact
    return Q(
        Q(contact_group__isnull=True, contact__isnull=True)
        | Q(contact_group_id=AnonymousContact.get_default_group().pk),
    )


class ProductCatalog:
    """
    A helper class to return products and shop products from the database
    """

    def __init__(self, context: Optional[ProductCatalogContext] = None):
        self.context = context or ProductCatalogContext()

    def _get_prices_filters(self):
        filters = Q()
        shop = self.context.shop
        supplier = self.context.supplier
        contact = self.context.contact
        user = self.context.user
        purchasable_only = self.context.purchasable_only

        if shop:
            filters &= Q(shop=shop)
        if supplier:
            filters &= Q(supplier=supplier)
        if purchasable_only:
            filters &= Q(is_available=True, is_visible=True)

        if not user and contact and hasattr(contact, "user"):
            user = contact.user

        user_all_seeing = is_user_all_seeing(user) if user else False

        # user can't see everything
        if not user_all_seeing:
            filters &= Q(
                Q(catalog_rule__isnull=True)
                | Q(catalog_rule__in=ProductCatalogPriceRule.objects.filter(get_price_contact_filter(contact)))
            )

        return filters

    def _get_discounted_prices_filters(self):
        now_dt = timezone.localtime(timezone.now())
        now_time = now_dt.time()

        filters = Q()
        shop = self.context.shop
        supplier = self.context.supplier

        if shop:
            filters &= Q(shop=shop)
        if supplier:
            filters &= Q(supplier=supplier)

        filters &= Q(
            catalog_rule__in=ProductCatalogDiscountedPriceRule.objects.filter(
                Q(get_discounted_price_contact_filter(self.context.contact)),
                Q(
                    Q(
                        valid_start_date__isnull=True,
                        valid_start_hour__isnull=True,
                    )
                    | Q(
                        valid_start_date__lte=now_dt,
                        valid_end_date__gt=now_dt,
                        valid_start_hour__isnull=True,
                    )
                    | Q(
                        valid_start_date__lte=now_dt,
                        valid_end_date__gt=now_dt,
                        valid_start_hour__lte=now_time,
                        valid_end_hour__gt=now_time,
                        valid_weekday__isnull=True,
                    )
                    | Q(
                        valid_start_date__lte=now_dt,
                        valid_end_date__gt=now_dt,
                        valid_start_hour__lte=now_time,
                        valid_end_hour__gt=now_time,
                        valid_weekday=now_dt.weekday(),
                    ),
                ),
            )
        )
        return filters

    def annotate_products_queryset(
        self, queryset: "QuerySet[Product]", annotate_discounts: bool = True
    ) -> "QuerySet[Product]":
        """
        Returns the given Product queryset annotated with price and discounted price.
        The catalog will filter the products according to the `context`.

            - `catalog_price` -> the cheapest price found for the context
            - `catalog_discounted_price` -> the cheapest discounted price found for the context
        """
        product_prices = (
            ProductCatalogPrice.objects.filter(product=OuterRef("pk"))
            .filter(self._get_prices_filters())
            .order_by("price_value")
        )

        queryset = queryset.annotate(
            catalog_price=Subquery(product_prices.values("price_value")[:1]),
        )

        if annotate_discounts:
            product_discounted_prices = (
                ProductCatalogDiscountedPrice.objects.filter(product=OuterRef("pk"))
                .filter(self._get_discounted_prices_filters())
                .order_by("discounted_price_value")
            )
            queryset = queryset.annotate(
                catalog_discounted_price=Subquery(product_discounted_prices.values("discounted_price_value")[:1]),
            )
        return queryset

    def get_products_queryset(self, annotate_discounts: bool = True) -> "QuerySet[Product]":
        """
        Returns a queryset of Product annotated with price and discounted price:
        The catalog will filter the products according to the `context`.

            - `catalog_price` -> the cheapest price found for the context
            - `catalog_discounted_price` -> the cheapest discounted price found for the context
        """
        return self.annotate_products_queryset(Product.objects.all(), annotate_discounts=annotate_discounts).filter(
            catalog_price__isnull=False
        )

    def annotate_shop_products_queryset(
        self, queryset: "QuerySet[ShopProduct]", annotate_discounts: bool = True
    ) -> "QuerySet[ShopProduct]":
        """
        Returns a the given ShopProduct queryset annotated with price and discounted price:
        The catalog will filter the shop products according to the `context`.

            - `catalog_price` -> the cheapest price found for the context
            - `catalog_discounted_price` -> the cheapest discounted price found for the context
        """
        product_prices = (
            ProductCatalogPrice.objects.filter(product=OuterRef("product_id"), shop=OuterRef("shop_id"))
            .filter(self._get_prices_filters())
            .order_by("price_value")
        )

        queryset = queryset.annotate(
            # as we are filtering ShopProducts, we can fallback to default_price_value
            # when the product is a variation parent (this is not possible with product queryset)
            catalog_price=Subquery(product_prices.values("price_value")[:1]),
        )
        if annotate_discounts:
            product_discounted_prices = (
                ProductCatalogDiscountedPrice.objects.filter(product=OuterRef("product_id"))
                .filter(self._get_discounted_prices_filters())
                .order_by("discounted_price_value")
            )
            queryset = queryset.annotate(
                catalog_discounted_price=Subquery(product_discounted_prices.values("discounted_price_value")[:1]),
            )

        return queryset

    def get_shop_products_queryset(
        self,
        annotate_discounts: bool = True,
        visibility: Optional[ShopProductVisibility] = None,
    ) -> "QuerySet[ShopProduct]":
        """
        Returns a queryset of ShopProduct annotated with price and discounted price:
        The catalog will filter the shop products according to the `context`.

        `visibility` the shop products visibility. If set to None, all
            products for any visibility will be returned.

            - `catalog_price` -> the cheapest price found for the context
            - `catalog_discounted_price` -> the cheapest discounted price found for the context,
                when configured to be annotate
        """
        shop_products = ShopProduct.objects.all()

        if visibility and visibility not in (ShopProductVisibility.ALWAYS_VISIBLE, ShopProductVisibility.NOT_VISIBLE):
            shop_products = shop_products.filter(visibility__in=[visibility, ShopProductVisibility.ALWAYS_VISIBLE])

        return self.annotate_shop_products_queryset(shop_products, annotate_discounts=annotate_discounts).filter(
            catalog_price__isnull=False
        )

    @classmethod
    def index_product(cls, product: Union[Product, int]):
        """
        Index the prices for the given `product`
        which can be either a Product instance or a product ID.
        """
        for shop_product in ShopProduct.objects.filter(product=product):
            cls.index_shop_product(shop_product)

    @classmethod
    def index_shop_product(cls, shop_product: Union[Product, int], **kwargs):
        """
        Index the prices for the given `shop_product`
        which can be either a ShopProduct instance or a shop product ID.

        This method will forward the indexing for the default pricing module
        and then trigger a signal for other apps to do their job if they need.
        """
        pricing_module = get_pricing_module()
        pricing_module.index_shop_product(shop_product)
        for discount_module in get_discount_modules():
            discount_module.index_shop_product(shop_product)
        index_catalog_shop_product.send(sender=cls, shop_product=shop_product)

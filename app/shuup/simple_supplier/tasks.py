# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from typing import Optional, Union

from shuup.core.models import Product, ProductCatalogPrice, ShopProduct, Supplier, SupplierShop


def index_product(product: Union[Product, int], supplier: Optional[Union[Supplier, int]] = None):
    product_id = product if not isinstance(product, Product) else product.pk
    shop_products = ShopProduct.objects.filter(product_id=product_id)
    if supplier:
        shop_products = shop_products.filter(suppliers=supplier)
    for shop_product in shop_products:
        index_shop_product(shop_product=shop_product)


def update_shop_product_stocks(shop_product: Union[ShopProduct, int], supplier_id=None):
    from shuup.simple_supplier.module import SimpleSupplierModule

    if not isinstance(shop_product, ShopProduct):
        shop_product = ShopProduct.objects.select_related("product").get(pk=shop_product)

    suppliers = Supplier.objects.filter(
        shop_products=shop_product.pk, supplier_modules__module_identifier=SimpleSupplierModule.identifier
    ).distinct()
    if supplier_id:
        suppliers = suppliers.filter(pk=supplier_id)
    for supplier in suppliers:
        supplier.update_stock(product_id=shop_product.product_id)


def update_product_stocks(product: Union[Product, int], supplier_id=None):
    from shuup.simple_supplier.module import SimpleSupplierModule

    suppliers = Supplier.objects.filter(
        shop_products__product_id=product, supplier_modules__module_identifier=SimpleSupplierModule.identifier
    ).distinct()
    if supplier_id:
        suppliers = suppliers.filter(pk=supplier_id)
    for supplier in suppliers:
        supplier.update_stock(product_id=product)


def index_supplier_shop_products(shop_id: int, supplier_id: int):
    for shop_product in ShopProduct.objects.filter(shop_id=shop_id, suppliers=supplier_id).select_related("product"):
        index_shop_product(shop_product, supplier_id)


def index_shop_product(shop_product: Union[ShopProduct, int], supplier_id: Optional[int] = None):
    # get all the suppliers that are linked to the shop product
    # that has the simple_supplier module
    from shuup.simple_supplier.module import SimpleSupplierModule

    if not isinstance(shop_product, ShopProduct):
        shop_product = ShopProduct.objects.select_related("product").get(pk=shop_product)

    suppliers = (
        Supplier.objects.filter(
            shop_products=shop_product.pk, supplier_modules__module_identifier=SimpleSupplierModule.identifier
        )
        .distinct()
        .only("pk", "module_data")
    )

    if supplier_id:
        suppliers = suppliers.filter(pk=supplier_id)

    for supplier in suppliers:
        is_purchasable = all(
            [
                supplier.enabled,
                SupplierShop.objects.filter(shop_id=shop_product.shop_id, supplier=supplier, is_approved=True).exists(),
                shop_product.purchasable,
            ]
        )

        # check whether there are other orderability issues
        if is_purchasable:
            has_orderability_errors = next(
                supplier.get_orderability_errors(shop_product, shop_product.minimum_purchase_quantity or 1), False
            )
            if has_orderability_errors:
                is_purchasable = False

        ProductCatalogPrice.objects.filter(
            product_id=shop_product.product_id, shop_id=shop_product.shop_id, supplier_id=supplier.pk
        ).update(is_available=is_purchasable)

    if shop_product.product.is_variation_parent():
        # also index child products
        children_shop_product = ShopProduct.objects.filter(
            product__variation_parent_id=shop_product.product_id, shop_id=shop_product.shop_id
        )
        for child_shop_product in children_shop_product:
            index_shop_product(child_shop_product)

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from shuup.admin.modules.orders.receivers import handle_custom_payment_return_requests
from shuup.admin.setting_keys import (
    SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION,
    SHUUP_ADMIN_ALLOW_HTML_IN_SUPPLIER_DESCRIPTION,
)
from shuup.admin.signals import object_saved
from shuup.core import cache
from shuup.core.models import Product, ProductCatalogPrice, ShopProduct, Supplier, SupplierModule
from shuup.core.order_creator.signals import order_creator_finished
from shuup.core.signals import shuup_initialized
from shuup.core.tasks import run_task


@receiver(shuup_initialized)
def on_shuup_initialized(sender, **kwargs):
    from shuup import configuration

    configuration.set(None, SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION, True)
    configuration.set(None, SHUUP_ADMIN_ALLOW_HTML_IN_SUPPLIER_DESCRIPTION, True)


@receiver(m2m_changed, sender=get_user_model().groups.through)
def on_user_groups_change(instance, action, model, **kwargs):
    from shuup.admin.utils.permissions import USER_PERMISSIONS_CACHE_NAMESPACE

    # a group has changed it's users relation through group.users.set()
    # then we need to bump the entire cache
    if isinstance(instance, Group):
        cache.bump_version(USER_PERMISSIONS_CACHE_NAMESPACE)

    # bump only the user's permission cache
    elif isinstance(instance, get_user_model()):
        cache.bump_version("{}:{}".format(USER_PERMISSIONS_CACHE_NAMESPACE, instance.pk))


@receiver(object_saved)
def on_object_saved(sender, object, **kwargs):
    # make sure to index the prices of the product when a product is saved
    if isinstance(object, ShopProduct):
        transaction.on_commit(
            lambda: run_task("shuup.core.catalog.tasks.index_shop_product", shop_product_id=object.pk)
        )

    if isinstance(object, Product):
        transaction.on_commit(lambda: run_task("shuup.core.catalog.tasks.index_product", product_id=object.pk))


@receiver(m2m_changed, sender=Supplier.supplier_modules.through)
def on_supplier_modules_changed(instance, pk_set, **kwargs):
    """
    Trigger signal to reindex products as the supplier module has changed
    """
    from shuup.admin.modules.suppliers.signals import supplier_products_reindex_required

    def check_supplier_no_module(supplier):
        if not supplier.supplier_modules.exists():
            # disable all products that doesn't have suppliers modules
            ProductCatalogPrice.objects.filter(supplier=supplier).update(is_available=False)
            return True

        return False

    if isinstance(instance, Supplier):
        if not check_supplier_no_module(instance):
            for shop in instance.shops.all().iterator():
                supplier_products_reindex_required.send(sender=type(instance), shop=shop, supplier=instance)

    elif isinstance(instance, SupplierModule):
        for supplier in Supplier.objects.filter(pk__in=pk_set):
            if check_supplier_no_module(supplier):
                continue

            for shop in supplier.shops.all():
                supplier_products_reindex_required.send(sender=type(instance), shop=shop, supplier=instance)


order_creator_finished.connect(handle_custom_payment_return_requests, dispatch_uid="shuup.admin.handle_cash_payments")

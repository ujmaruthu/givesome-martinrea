# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from six import string_types

from shuup.admin.modules.products.views.list import ProductListView
from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.mass_action import BaseExportCSVMassAction
from shuup.admin.utils.picotable import PicotableMassAction, PicotableRedirectMassAction
from shuup.core.catalog import ProductCatalog
from shuup.core.models import Shop, ShopProduct, ShopProductVisibility
from shuup.core.signals import context_cache_item_bumped
from shuup.core.utils import context_cache
from shuup.utils.django_compat import reverse


class VisibleMassAction(PicotableMassAction):
    label = _("Set visible")
    identifier = "mass_action_product_visible"

    def process(self, request, ids):
        shop = get_shop(request)

        if isinstance(ids, string_types) and ids == "all":
            query = Q(shop=shop)
        else:
            query = Q(pk__in=ids, shop=shop)

        ShopProduct.objects.filter(query).update(visibility=ShopProductVisibility.ALWAYS_VISIBLE)

        for shop_product in ShopProduct.objects.only("pk").filter(query).iterator():
            ProductCatalog.index_shop_product(shop_product.pk)
            context_cache.bump_cache_for_shop_product(shop_product)
            context_cache_item_bumped.send(sender=Shop, shop_id=shop.pk)


class InvisibleMassAction(PicotableMassAction):
    label = _("Set invisible")
    identifier = "mass_action_product_invisible"

    def process(self, request, ids):
        shop = get_shop(request)
        if isinstance(ids, string_types) and ids == "all":
            query = Q(shop=shop)
        else:
            query = Q(pk__in=ids, shop=shop)

        ShopProduct.objects.filter(query).update(visibility=ShopProductVisibility.NOT_VISIBLE)

        for shop_product in ShopProduct.objects.only("pk").filter(query).iterator():
            ProductCatalog.index_shop_product(shop_product.pk)
            context_cache.bump_cache_for_shop_product(shop_product)
            context_cache_item_bumped.send(sender=Shop, shop_id=shop.pk)


class ExportProductsCSVAction(BaseExportCSVMassAction):
    identifier = "mass_action_export_product_csv"
    model = ShopProduct
    view_class = ProductListView
    filename = "products.csv"


class EditProductAttributesAction(PicotableRedirectMassAction):
    label = _("Edit products")
    identifier = "mass_action_edit_product"
    redirect_url = reverse("shuup_admin:shop_product.mass_edit")

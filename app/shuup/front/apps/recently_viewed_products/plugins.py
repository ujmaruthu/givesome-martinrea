# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.core.catalog import ProductCatalog, ProductCatalogContext
from shuup.core.models import ProductMode, ShopProductVisibility
from shuup.core.utils.static import get_shuup_static_url
from shuup.xtheme import TemplatedPlugin
from shuup.xtheme.resources import add_resource


class RecentlyViewedProductsPlugin(TemplatedPlugin):
    identifier = "recently_viewed_products"
    name = _("Recently Viewed Products List")
    template_name = "shuup/recently_viewed_products/list_view.jinja"

    def get_context_data(self, context):
        context = super().get_context_data(context)
        request = context["request"]
        product_ids = [int(pid) for pid in request.COOKIES.get("rvp", "").split(",") if pid != ""]

        catalog = ProductCatalog(
            ProductCatalogContext(
                shop=request.shop,
                user=getattr(request, "user", None),
                contact=getattr(request, "customer", None),
            )
        )
        context["products"] = sorted(
            catalog.get_products_queryset().filter(
                id__in=product_ids,
                mode__in=ProductMode.get_parent_modes(),
                shop_products__visibility__in=[ShopProductVisibility.LISTED, ShopProductVisibility.ALWAYS_VISIBLE],
            )[:20],
            key=lambda p: product_ids.index(p.pk),
        )
        return context


def add_resources(context, content):
    view_class = getattr(context["view"], "__class__", None) if context.get("view") else None
    if not view_class:
        return
    view_name = getattr(view_class, "__name__", "")
    if view_name == "ProductDetailView":
        add_resource(context, "body_end", get_shuup_static_url("shuup/recently_viewed_products/lib.js"))

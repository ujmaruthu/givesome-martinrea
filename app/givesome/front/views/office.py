# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.core.models import CategoryStatus, ShopProductVisibility

from givesome.front.views.supplier import GivesomeBaseBrandView
from givesome.models import GivesomeOffice, GivesomePromotedProduct


class GivesomeOfficeView(GivesomeBaseBrandView):
    template_name = "givesome/shuup/front/supplier/office.jinja"

    def get_queryset(self):
        return GivesomeOffice.objects.filter(
            disabled=False,
            supplier__enabled=True,
            supplier__deleted=False,
            supplier__supplier_shops__is_approved=True,
        )

    def _get_sustainability_goals(self):
        if hasattr(self.object, "office_sustainability_goals"):
            return self.object.office_sustainability_goals.goals.all()
        return []

    def _get_filter_category_ids(self):
        return (
            self.object.promoted_projects.filter(
                shop_product__shop=self.request.shop,
                shop_product__primary_category__isnull=False,
                shop_product__primary_category__status=CategoryStatus.VISIBLE,
                shop_product__product__deleted=False,
                shop_product__visibility=ShopProductVisibility.ALWAYS_VISIBLE,
            )
            .values_list("shop_product__primary_category")
            .distinct()
        )

    def _custom_product_filter(self, qs):
        return qs.filter(shop_products__promotions__office=self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["brand"] = self.object
        context["promoter"] = self.object
        context["supplier"] = self.object.supplier
        context["offices"] = self.object.get_children().filter(disabled=False).order_by("ordering")
        context["office_term"] = self.object.supplier.office_terms.filter(level=self.object.level + 1).first()
        # Override normal ordering
        context["products"] = [
            promoted_project.shop_product.product
            for promoted_project in GivesomePromotedProduct.objects.filter(
                office=self.object, shop_product__product__in=context["products"]
            ).order_by("ordering")
        ]
        return context

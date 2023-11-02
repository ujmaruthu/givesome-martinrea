# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from shuup.admin.modules.products.views import ProductEditView
from shuup.admin.modules.products.views import ProductListView as AdminProductListView
from shuup.admin.modules.products.views.edit import (
    ProductAttributeFormPart,
    ProductImageMediaFormPart,
    ProductMediaFormPart,
)
from shuup.admin.utils.picotable import ChoicesFilter, Column, RangeFilter, TextFilter
from shuup.core.models import ProductMode
from shuup_multivendor.admin_module.views import ProductListView as VendorProductListView

from givesome.admin_module.form_parts.product import (
    GivesomeAdminProductBaseFormPart,
    GivesomeAdminShopProductFormPart,
    GivesomeProjectExtraFormPart,
    GivesomeShopProductSustainabilityGoalFormPart,
)
from givesome.admin_module.utils import HasValueFilter


class GivesomeAdminProductListView(AdminProductListView):
    def __init__(self):
        super().__init__()
        self.columns.append(
            Column(
                "progress",
                _("Goal Progress"),
                display="format_goal_progress",
                filter_config=HasValueFilter(
                    filter_field="product__project_extra__fully_funded_date",
                    labels={"true": _("Complete"), "false": _("Incomplete")},
                ),
                ordering=8,
                raw=True,
            ),
        )

    def format_goal_progress(self, instance):
        if hasattr(instance.product, "project_extra"):
            goal = instance.product.project_extra.goal_amount
            current = instance.product.project_extra.goal_progress_amount
            percentage = instance.product.project_extra.goal_progress_percentage
            date = instance.product.project_extra.fully_funded_date
            if date is not None:
                date = f'<br>Fully funded on: {date.strftime("%Y-%m-%d")}'
            else:
                date = ""
            return f"{percentage}%, (${current} / ${goal}){date}"
        return ""

    def get_queryset(self):
        qs = super().get_queryset()
        filter = self.get_filter()

        givesome_valid_project = filter.get("givesome_valid_project")
        if givesome_valid_project:
            qs = qs.filter(
                product__project_extra__goal_amount__isnull=False,
                suppliers__isnull=False,
                suppliers__deleted=False,
                suppliers__supplier_shops__is_approved=True,
            )

        has_video = filter.get("has_video")
        if has_video:
            qs = qs.filter(product__completion_videos__isnull=False)

        recently_funded_first = filter.get("recently_funded_first")
        if recently_funded_first:
            qs = qs.order_by("-product__project_extra__fully_funded_date")

        return qs


class GivesomeProductListView(VendorProductListView):
    default_columns = [
        Column(
            "primary_image",
            _("Primary Image"),
            display="get_primary_image",
            class_name="text-center",
            raw=True,
            ordering=1,
            sortable=False,
        ),
        Column(
            "name",
            _("Name"),
            sort_field="product__translations__name",
            display="get_name",
            filter_config=TextFilter(filter_field="product__translations__name", placeholder=_("Filter by name...")),
            ordering=2,
        ),
        Column(
            "sku", _("SKU"), display="product__sku", filter_config=RangeFilter(filter_field="product__sku"), ordering=3
        ),
        Column(
            "mode", _("Mode"), display="product__mode", filter_config=ChoicesFilter(ProductMode.choices), ordering=5
        ),
        Column(
            "primary_category",
            _("Location"),
            display=(lambda instance: instance.primary_category.name if instance.primary_category else None),
            filter_config=TextFilter(
                filter_field="primary_category__translations__name", placeholder=_("Filter by category name...")
            ),
            ordering=6,
        ),
        Column(
            "progress",
            _("Goal Progress"),
            display="format_goal_progress",
            filter_config=HasValueFilter(
                filter_field="product__project_extra__fully_funded_date",
                labels={"true": _("Complete"), "false": _("Incomplete")},
            ),
            ordering=7,
            raw=True,
        ),
    ]

    def format_goal_progress(self, instance):
        if hasattr(instance.product, "project_extra"):
            goal = instance.product.project_extra.goal_amount
            current = instance.product.project_extra.goal_progress_amount
            percentage = instance.product.project_extra.goal_progress_percentage
            date = instance.product.project_extra.fully_funded_date
            if date is not None:
                date = f'<br>Fully funded on: {date.strftime("%Y-%m-%d")}'
            else:
                date = ""
            return f"{percentage}%, (${current} / ${goal}){date}"
        return ""


class GivesomeAdminProductEditView(ProductEditView):
    base_form_part_classes = [
        GivesomeAdminProductBaseFormPart,
        GivesomeAdminShopProductFormPart,
        ProductAttributeFormPart,
        ProductImageMediaFormPart,
        ProductMediaFormPart,
        GivesomeShopProductSustainabilityGoalFormPart,
        GivesomeProjectExtraFormPart,
    ]

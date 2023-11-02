# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.http import Http404, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.core.models import ShopProduct, ShopProductVisibility
from shuup_multivendor.admin_module.views import ProductListView


class PrimaryProjectListView(ProductListView):  # TODO: Project promote view for suppliers
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
            display="get_name",
            raw=True,
            filter_config=TextFilter(filter_field="product__translations__name", placeholder=_("Filter by name...")),
        ),
        Column(
            "description",
            _("Short Description"),
            display="get_description",
        ),
        Column(
            "supplier",
            _("Charity"),
            display="get_supplier_name",
            filter_config=TextFilter(filter_field="suppliers__name", placeholder=_("Filter by charity...")),
        ),
        Column(
            "primary_category",
            _("Location"),
            display=(lambda instance: instance.primary_category.name if instance.primary_category else None),
            filter_config=TextFilter(
                filter_field="primary_category__translations__name", placeholder=_("Filter by location name...")
            ),
        ),
        Column(
            "progress",
            _("Goal Progress"),
            display="format_goal_progress",
            ordering=8,
            raw=True,
        ),
        Column(
            "primary",
            _("Set as Primary"),
            display="get_primary_button",
            ordering=15,
            sortable=False,
            linked=True,
            raw=True,
        ),
    ]

    def get_object_url(self, instance):
        return None  # No edit for primary projects

    def get_name(self, instance):
        name = instance.product.safe_translation_getter("name")
        front_url = reverse("shuup:product", kwargs={"pk": instance.product.pk, "slug": instance.product.slug})
        if instance.visibility is not ShopProductVisibility.NOT_VISIBLE:
            return f'<a href="{front_url}">{name}</a>'
        return f"{name}"

    def get_description(self, instance):
        return instance.product.safe_translation_getter("short_description")

    def get_supplier_name(self, instance):
        return instance.suppliers.first().name

    def get_primary_button(self, instance):
        context = self._get_primary_context(instance)
        return render_to_string("givesome/admin/projects/primary_button.jinja", context=context, request=self.request)

    def _get_primary_context(self, instance):
        supplier = get_supplier(self.request)
        primary = supplier.givesome_extra.primary_project == instance
        has_primary = supplier.givesome_extra.primary_project is not None
        if not primary and not has_primary:
            text = _("Set as primary project")
        else:
            text = _("Remove as primary project")

        return {"text": text, "is_primary": primary, "instance": instance, "chooser_id": supplier.id, "kind": "vendor"}

    def get_queryset(self):
        supplier = get_supplier(self.request)
        return ShopProduct.objects.filter(id__in=supplier.offices.all().values("promoted_projects__shop_product_id"))


class SetVendorPrimaryView(View):
    def post(self, request, *args, **kwargs):
        self.supplier = get_supplier(self.request)
        if self.supplier is None:
            raise Http404()

        self.project = ShopProduct.objects.filter(pk=int(request.POST.get("productId"))).first()
        if self.project is None:
            raise Http404()

        is_primary = False
        if self.supplier.givesome_extra.primary_project == self.project:
            self.supplier.givesome_extra.primary_project = None
        else:
            self.supplier.givesome_extra.primary_project = self.project
            is_primary = True
        self.supplier.givesome_extra.save()

        if request.is_ajax():
            return JsonResponse({"is_primary": is_primary})

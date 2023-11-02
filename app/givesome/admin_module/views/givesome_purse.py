# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db.models import Q
from django.http.response import Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.picotable import Column
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup.core.models import ProductMode, ShopProduct
from shuup_multivendor.admin_module.views.products import ProductListView
from shuup_multivendor.utils.product import filter_approved_shop_products

from givesome.admin_module.form_parts.givesome_purse import GivesomePurseAllocationManualFormPart
from givesome.admin_module.views.project_promote import ProjectPromoteEditView
from givesome.models import GivesomePurse, GivesomePurseAllocation


class GivesomePurseListView(PicotableListView):
    model = GivesomePurse
    url_identifier = "givesome_purse"
    columns = [
        Column(
            "name",
            _("Name"),
            ordering=1,
            sortable=True,
        ),
        Column(
            "balance",
            _("Balance"),
            display="get_balance",
            ordering=4,
            sortable=True,
        ),
    ]

    def __init__(self):
        """To keep columns as-is"""
        pass

    def get_balance(self, instance):
        """Show 0 balance. Otherwise field would be blank"""
        if instance.balance == 0:
            return "$ 0"
        return f"$ {instance.balance}"

    def get_toolbar(self):
        return None

    def get_object_url(self, instance):
        return reverse("shuup_admin:givesome_purse.project_list", kwargs=dict(pk=instance.pk))

    def get_queryset(self):
        return super().get_queryset().filter(Q(supplier__isnull=True) | Q(supplier__givesome_extra__allow_purse=True))


class GivesomePurseProjectListView(ProjectPromoteEditView):
    def __init__(self):
        self.default_columns = [col for col in self.default_columns if col.id not in ["primary", "promoting"]]
        super().__init__()

    def get_toolbar(self):
        return None

    def get_object_url(self, instance):
        return reverse("shuup_admin:givesome_purse.edit", kwargs=dict(pk=self.kwargs.get("pk"), project_id=instance.pk))

    def get_context_data(self, **kwargs):
        context = ProductListView.get_context_data(self, **kwargs)
        supplier = get_supplier(self.request)

        purse_qs = GivesomePurse.objects.filter(id=self.kwargs.get("pk"))
        if supplier:
            purse_qs = purse_qs.filter(supplier=supplier)
        purse = purse_qs.first()

        if purse is None:
            return Http404()

        context["title"] = f"{purse.name} (${purse.balance})"
        return context


class GivesomePurseAllocationEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = GivesomePurseAllocation
    template_name = "givesome/admin/givesome_purse/edit.jinja"
    context_object_name = "allocation"
    add_form_errors_as_messages = True
    base_form_part_classes = [
        # GivesomePurseAllocationBaseFormPart, TODO Form is hidden until automatic donation is implemented
        GivesomePurseAllocationManualFormPart
    ]

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        return get_default_edit_toolbar(self, save_form_id, with_split_save=False, with_save_as_copy=False)

    def get_object(self, queryset=None):
        # Make sure user didn't navigate to some invalid project
        purse_id = self.kwargs.get("pk")
        shop_product_id = self.kwargs.get("project_id")
        valid_project = filter_approved_shop_products(
            ShopProduct.objects.filter(
                product__deleted=False, pk=shop_product_id, suppliers__deleted=False, product__mode=ProductMode.NORMAL
            )
        ).exists()
        if not valid_project:
            raise Http404()

        # Automatically create GivesomePurseAllocation object when page is loaded
        return GivesomePurseAllocation.objects.get_or_create(
            purse_id=purse_id,
            shop_product_id=shop_product_id,
        )[0]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context

    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_success_url(self):
        return reverse("shuup_admin:givesome_purse.project_list", kwargs=dict(pk=self.kwargs.get("pk")))

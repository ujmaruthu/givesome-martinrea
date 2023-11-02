# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.modules.products.views.edit import ProductBaseFormPart, ShopProductFormPart
from shuup.core.models import Product, ShopProduct
from shuup_multivendor.admin_module.form_parts.product import VendorProductBaseFormPart, VendorShopProductFormPart

from givesome.admin_module.form_parts.sustainability_goal_selection import SustainabilityGoalSelectionFormSet
from givesome.admin_module.forms.product import (
    GivesomeAdminProductBaseForm,
    GivesomeAdminShopProductForm,
    GivesomeVendorProductBaseForm,
    GivesomeVendorShopProductForm,
    ProjectExtraForm,
)
from givesome.models import ProjectSustainabilityGoals


class GivesomeVendorProductBaseFormPart(VendorProductBaseFormPart):
    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            GivesomeVendorProductBaseForm,
            template_name="shuup_multivendor/admin/products/_edit_base_form.jinja",
            required=True,
            kwargs={
                "instance": self.object.product,
                "languages": settings.LANGUAGES,
                "initial": self.get_initial(),
                "request": self.request,
            },
        )
        yield TemplatedFormDef(
            "base_extra",
            forms.Form,
            template_name="shuup_multivendor/admin/products/_edit_extra_base_form.jinja",
            required=False,
        )

    def get_sku(self):
        sku = self.request.GET.get("sku", "")
        if not sku:
            last_id = Product.objects.values_list("id", flat=True).first()
            sku = last_id + 1 if last_id else 1000
        return sku


class GivesomeVendorShopProductFormPart(VendorShopProductFormPart):
    def get_form_defs(self):
        yield TemplatedFormDef(
            "shop%d" % self.shop.pk,
            GivesomeVendorShopProductForm,
            template_name="shuup_multivendor/admin/products/_edit_shop_form.jinja",
            required=True,
            kwargs={
                "instance": self.object,
                "initial": self.get_initial(),
                "request": self.request,
                "languages": settings.LANGUAGES,
            },
        )

        # the hidden extra form template that uses ShopProductForm
        yield TemplatedFormDef(
            "shop%d_extra" % self.shop.pk,
            forms.Form,
            template_name="shuup_multivendor/admin/products/_edit_extra_shop_form.jinja",
            required=False,
        )


class GivesomeShopProductSustainabilityGoalFormPart(VendorProductBaseFormPart):
    name = "sustainability goals"

    def get_initial(self):
        return ProjectSustainabilityGoals.objects.filter(project=self.object)

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            SustainabilityGoalSelectionFormSet,
            template_name="givesome/admin/sustainability_goal/sustainability_goal_project_selection.jinja",
            required=False,
            kwargs={"initial": self.get_initial()},
        )

    def form_valid(self, form_group):
        goals = form_group.cleaned_data.get(self.name)
        shop_product = ShopProduct.objects.filter(product=self.object, shop=self.request.shop).first()
        project_goals, __ = ProjectSustainabilityGoals.objects.get_or_create(project=shop_product)

        # Associate only the goals selected just now.
        if goals:
            project_goals.goals.set(goals["sustainability_goals"])
        else:
            project_goals.goals.clear()
        return super().form_valid(form_group)


class GivesomeAdminProductBaseFormPart(ProductBaseFormPart):
    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            GivesomeAdminProductBaseForm,
            template_name="shuup/admin/products/_edit_base_form.jinja",
            required=True,
            kwargs={
                "instance": self.object.product,
                "languages": settings.LANGUAGES,
                "initial": self.get_initial(),
                "request": self.request,
            },
        )

        yield TemplatedFormDef(
            "base_extra", forms.Form, template_name="shuup/admin/products/_edit_extra_base_form.jinja", required=False
        )

    def get_sku(self):
        sku = self.request.GET.get("sku", "")
        if not sku:
            last_id = Product.objects.values_list("id", flat=True).first()
            sku = last_id + 1000 if last_id else 1000
        return sku


class GivesomeAdminShopProductFormPart(ShopProductFormPart):
    def get_form_defs(self):
        yield TemplatedFormDef(
            "shop%d" % self.shop.pk,
            GivesomeAdminShopProductForm,
            template_name="shuup/admin/products/_edit_shop_form.jinja",
            required=True,
            kwargs={
                "instance": self.object,
                "initial": self.get_initial(),
                "request": self.request,
                "languages": settings.LANGUAGES,
            },
        )

        # the hidden extra form template that uses ShopProductForm
        yield TemplatedFormDef(
            "shop%d_extra" % self.shop.pk,
            forms.Form,
            template_name="shuup/admin/products/_edit_extra_shop_form.jinja",
            required=False,
        )


class GivesomeProjectExtraFormPart(FormPart):
    def get_form_defs(self):
        yield TemplatedFormDef(
            "project_extra",
            ProjectExtraForm,
            template_name="givesome/admin/projects/project_extra.jinja",
            required=True,
            kwargs={
                "instance": self.object.product,
                "shop": self.request.shop,
            },
        )

    def form_valid(self, form):
        extra_form = form["project_extra"]
        if not extra_form.changed_data:
            return
        extra_form.save(request=self.request)

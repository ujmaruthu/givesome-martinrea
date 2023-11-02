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
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from shuup.admin.modules.products.forms import ProductBaseForm, ShopProductForm
from shuup.core.models import ProductType, ShippingMode, ShopProductVisibility, Supplier
from shuup_multivendor.admin_module.forms.product import VendorProductBaseForm, VendorShopProductForm

from givesome.admin_module.forms.shop_settings import givesome_promote_invisible
from givesome.enums import VendorExtraType
from givesome.models import GivesomePromotedProduct, ProjectExtra
from givesome.models.project_extra import ensure_project_extra


class GivesomeVendorProductBaseForm(VendorProductBaseForm):
    class Meta(VendorProductBaseForm.Meta):
        widgets = VendorProductBaseForm.Meta.widgets
        widgets.update(
            {
                "sales_unit": forms.HiddenInput(),
                "shipping_mode": forms.HiddenInput(),
                "tax_class": forms.HiddenInput(),
            }
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pops = ["barcode", "depth", "gross_weight", "gtin", "height", "manufacturer", "net_weight", "width", "type"]
        for field in pops:
            self.fields.pop(field)

    def save(self, commit=True):
        instance = super().save()
        if instance.type is None:
            instance.type = ProductType.objects.first()
            instance.save()
        return instance


class GivesomeVendorShopProductForm(VendorShopProductForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pops = [
            "discount_amount",
            "minimum_price_value",
            "purchase_multiple",
            "backorder_maximum",
            "display_unit",
            "limit_shipping_methods",
            "shipping_methods",
            # Projects should have only one category, primary category is always added to categories
            # Because category field is removed, no need to clear them when primary_category is changed
            "categories",
        ]
        for field in pops:
            self.fields.pop(field)

        hidden = [
            "minimum_purchase_quantity",
            "supplier_price",
        ]
        for field in hidden:
            self.fields[field].widget = forms.HiddenInput()

        self.fields["supplier_price"].disabled = True
        self.initial["supplier_price"] = 1
        self.fields["primary_category"].label = _("Location")

        self.initial["shipping_mode"] = ShippingMode.NOT_SHIPPED

    def save(self, commit=True):
        if self.instance.visibility != ShopProductVisibility.ALWAYS_VISIBLE:
            # If visibility is reduced, remove all project promotions
            if givesome_promote_invisible(self.instance.shop):
                self.instance.primary_offices.clear()
                self.instance.primary_suppliers.clear()
                GivesomePromotedProduct.objects.filter(shop_product=self.instance).delete()
        return super().save()


class GivesomeAdminProductBaseForm(ProductBaseForm):
    class Meta(ProductBaseForm.Meta):
        widgets = ProductBaseForm.Meta.widgets
        widgets.update(
            {
                "sales_unit": forms.HiddenInput(),
                "shipping_mode": forms.HiddenInput(),
                "tax_class": forms.HiddenInput(),
            }
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pops = ["barcode", "depth", "gross_weight", "gtin", "height", "manufacturer", "net_weight", "width", "type"]
        for field in pops:
            self.fields.pop(field)

        if "file" in self.fields:  # Only available in new products
            self.fields["file"].widget.browsable = False  # Disable media browser

        self.initial["shipping_mode"] = ShippingMode.NOT_SHIPPED

    def save(self):
        instance = super().save()
        if instance.type is None:
            instance.type = ProductType.objects.first()
            instance.save()
        return instance


class GivesomeAdminShopProductForm(ShopProductForm):
    class Meta(ShopProductForm.Meta):
        widgets = {
            "minimum_purchase_quantity": forms.HiddenInput(),
            "tax_class": forms.HiddenInput(),
            "default_price_value": forms.HiddenInput(),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pops = [
            "minimum_price_value",
            "visibility_limit",
            "visibility_groups",
            "purchase_multiple",
            "backorder_maximum",
            "display_unit",
            "limit_shipping_methods",
            "limit_payment_methods",
            "shipping_methods",
            "payment_methods",
            # Projects should have only one category, primary category is always added to categories
            # Because category field is removed, no need to clear them when primary_category is changed
            "categories",
        ]
        for field in pops:
            self.fields.pop(field)

        self.initial["default_price_value"] = 1
        self.fields["default_price_value"].disabled = True
        self.fields["primary_category"].label = _("Location")

        self.fields["suppliers"] = ModelChoiceField(
            label=_("Charity"),
            help_text=_("The owner of this project. Changing the charity afterwards is not possible."),
            required=True,
            queryset=Supplier.objects.filter(
                givesome_extra__vendor_type=VendorExtraType.CHARITY,
                deleted=False,
                supplier_shops__is_approved=True,
            ),
        )
        self.initial["suppliers"] = (
            self.instance.suppliers.first().pk if self.instance.pk and self.instance.suppliers.first() else None
        )
        if self.instance.pk and self.instance.suppliers.exists():  # Changing supplier is not supported
            self.fields["suppliers"].disabled = True

    def clean(self):
        data = super().clean()
        if not self.instance.id:
            suppliers = data.get("suppliers")  # This is just a single charity supplier
            data["suppliers"] = [suppliers]

        # Goal tracking will break if supplier is changed on an existing shop_product
        # Setting the field disabled will raise a TypeError
        if self.instance.id and self.instance is not None:
            data.pop("suppliers", None)
        else:
            if not data.get("suppliers"):
                error_msg = _("Please select a charity with which to associate this new project.")
                self.add_error("suppliers", error_msg)
                raise ValidationError(error_msg)
        return data

    def save(self, commit=True):
        if self.instance.visibility != ShopProductVisibility.ALWAYS_VISIBLE:
            # If visibility is reduced, remove all project promotions
            if givesome_promote_invisible(self.instance.shop):
                self.instance.primary_offices.clear()
                self.instance.primary_suppliers.clear()
                GivesomePromotedProduct.objects.filter(shop_product=self.instance).delete()
        return super().save()


class ProjectExtraForm(forms.ModelForm):
    class Meta:
        model = ProjectExtra
        fields = (
            "goal_amount",
            "lives_impacted",
            "sponsored_by",
            "available_from",
            "enable_receipting",
            "donation_url",
        )

    def __init__(self, *args, **kwargs):
        shop = kwargs.pop("shop", None)
        super().__init__(*args, **kwargs)
        initial_goal = 0
        initial_impacted = 0
        initial_available_from = None
        initial_sponsored_by = None
        initial_enable_receipting = False
        initial_donation_url = None
        if self.instance.pk:
            extra = ensure_project_extra(self.instance)
            initial_goal = extra.goal_amount
            initial_impacted = extra.lives_impacted
            initial_available_from = extra.available_from
            initial_sponsored_by = extra.sponsored_by
            initial_enable_receipting = extra.enable_receipting
            initial_donation_url = extra.donation_url
            if extra.fully_funded_date:
                self.fields["goal_amount"].disabled = True
            if shop:
                shop_product = self.instance.get_shop_instance(shop)
                charity = shop_product.suppliers.first()
                if not charity.givesome_extra.enable_receipting:
                    self.fields["enable_receipting"].disabled = True
                    self.fields["enable_receipting"].initial = False
                    self.fields["enable_receipting"].help_text = _(
                        "To enable receipting for this project, please contact Givesome."
                    )
                else:
                    self.fields["enable_receipting"].initial = initial_enable_receipting

        self.fields["available_from"].initial = initial_available_from
        self.fields["goal_amount"].initial = initial_goal
        self.fields["lives_impacted"].initial = initial_impacted
        self.fields["sponsored_by"].initial = initial_sponsored_by
        self.fields["sponsored_by"].queryset = Supplier.objects.filter(deleted=False)
        self.fields["donation_url"].initial = initial_donation_url

    def clean(self):
        data = super().clean()
        if "goal_amount" not in data or data["goal_amount"] < 0:
            raise ValidationError("Goal amount must not be negative")
        return data

    def save(self, commit=True, request=None):
        instance = super().save()
        goal = self.cleaned_data["goal_amount"]
        shop_product = instance.get_shop_instance(request.shop)
        supplier = shop_product.suppliers.first()
        project_extra, created = ProjectExtra.objects.get_or_create(project=instance, defaults=dict(goal_amount=goal))
        project_extra.lives_impacted = self.cleaned_data["lives_impacted"]
        project_extra.sponsored_by = self.cleaned_data["sponsored_by"]
        project_extra.available_from = self.cleaned_data["available_from"]
        project_extra.enable_receipting = self.cleaned_data["enable_receipting"]
        project_extra.donation_url = self.cleaned_data["donation_url"]

        if created:
            # Just created, set stock to goal
            supplier.adjust_stock(instance.id, goal)
        else:
            # Goal modified, adjust stock by the delta
            supplier.adjust_stock(instance.id, goal - project_extra.goal_amount)

        # Use backorders to allow donating over the maximum
        # backorders are set to 0 after the last donation goes over the goal in signal_handlers
        if not project_extra.fully_funded_date:
            shop_product.backorder_maximum = goal * 2
            shop_product.save()
        project_extra.goal_amount = goal
        project_extra.save()
        return instance

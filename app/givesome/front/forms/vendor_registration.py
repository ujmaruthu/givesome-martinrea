# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.contrib.auth.models import Group
from django.forms import forms
from shuup.apps.provides import get_provide_objects
from shuup.core.models import Product, ProductMode, SalesUnit, ShippingMode, ShopProduct, SupplierModule, TaxClass
from shuup.core.pricing import TaxfulPrice
from shuup.simple_supplier.models import StockCount
from shuup_multivendor.forms import VendorRegistrationForm
from shuup_multivendor.models import SupplierUser

from givesome.enums import VendorExtraType
from givesome.models import ProjectExtra, VendorExtra


class GivesomeRegistrationCustomFieldsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # In case they want to add sustainability goals to registration
        provide_objects = list(get_provide_objects("givesome_charity_registration"))

        for provider_cls in provide_objects:
            provider = provider_cls()
            for definition in provider.get_fields(request=self.request):
                self.fields[definition.name] = definition.field


class GivesomeRegistrationForm(VendorRegistrationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add a custom form set with the givesome-specific fields (url)
        self.add_form_def(
            "vendor_extra", form_class=GivesomeRegistrationCustomFieldsForm, kwargs=dict(request=self.request)
        )


class CharityRegistrationForm(GivesomeRegistrationForm):
    def save(self, commit=True):
        vendor_user = super().save(commit=commit)

        # Now add Givesome-specific vendor info to the new charity.
        supplier_user = SupplierUser.objects.filter(user=vendor_user, shop=self.request.shop).first()
        supplier_user.supplier.supplier_modules.add(SupplierModule.objects.get(module_identifier="simple_supplier"))
        VendorExtra.objects.create(
            vendor=supplier_user.supplier,
            vendor_type=VendorExtraType.CHARITY,
            allow_brand_page=False,
            website_url=self.cleaned_data["vendor_extra"]["website_url"],
        )

        # Add user to correct permission group
        group = Group.objects.filter(name="Charity").first()
        vendor_user.groups.add(group)

        # Create a product dedicated to supporting this charity and an unpurchasable ShopProduct for promotion.
        name = "{:s} Monthly Donation".format(supplier_user.supplier.name)
        charity_support = Product.objects.create(
            name=name,
            slug="-".join(name.split(" ")),
            mode=ProductMode.SUBSCRIPTION,
            shipping_mode=ShippingMode.NOT_SHIPPED,
            sku="-".join(supplier_user.supplier.name.split(" ") + [str(supplier_user.supplier.id)]),
            tax_class=TaxClass.objects.filter(identifier="product").first(),
            sales_unit=SalesUnit.objects.filter(identifier="pcs").first(),
        )
        StockCount.objects.create(stock_managed=False, product=charity_support, supplier=supplier_user.supplier)
        ProjectExtra.objects.create(project=charity_support, goal_amount=0)
        support_display = ShopProduct.objects.create(
            default_price=TaxfulPrice(value=0, currency=self.request.shop.currency),
            product=charity_support,
            purchasable=False,
            shop=self.request.shop,
        )
        support_display.suppliers.add(supplier_user.supplier)
        return vendor_user


class PartnerRegistrationForm(GivesomeRegistrationForm):
    def save(self, commit=True):
        vendor_user = super().save(commit=commit)

        # Now add Givesome-specific vendor info to the new charity.
        supplier_user = SupplierUser.objects.filter(user=vendor_user, shop=self.request.shop).first()
        VendorExtra.objects.create(
            vendor=supplier_user.supplier,
            vendor_type=VendorExtraType.BRANDED_VENDOR,
            allow_brand_page=True,
            website_url=self.cleaned_data["vendor_extra"]["website_url"],
        )

        # Add user to correct permission group
        group = Group.objects.filter(name="Brand").first()
        vendor_user.groups.add(group)

        return vendor_user

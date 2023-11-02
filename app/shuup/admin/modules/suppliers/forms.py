# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

import bleach
from django import forms
from django.utils.translation import ugettext_lazy as _

from shuup import configuration
from shuup.admin.forms import ShuupAdminForm
from shuup.admin.forms.fields import ObjectSelect2MultipleField
from shuup.admin.forms.widgets import TextEditorWidget
from shuup.admin.modules.suppliers.signals import supplier_products_reindex_required
from shuup.admin.setting_keys import SHUUP_ADMIN_ALLOW_HTML_IN_SUPPLIER_DESCRIPTION
from shuup.admin.shop_provider import get_shop
from shuup.core.models import MutableAddress, Shop, Supplier, SupplierShop
from shuup.core.setting_keys import SHUUP_ENABLE_MULTIPLE_SUPPLIERS
from shuup.utils.django_compat import force_text


class SupplierBaseForm(ShuupAdminForm):
    class Meta:
        model = Supplier
        exclude = ("module_data", "options", "contact_address", "deleted")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(SupplierBaseForm, self).__init__(*args, **kwargs)

        # add shops field when superuser only
        if getattr(self.request.user, "is_superuser", False):
            initial_shops = self.instance.shops.all() if self.instance.pk else []
            self.fields["shops"] = ObjectSelect2MultipleField(
                label=_("Shops"),
                help_text=_("Select shops for this supplier. Keep it blank to share with all shops."),
                model=Shop,
                required=False,
                initial=initial_shops,
            )
            self.fields["shops"].choices = initial_shops
            self.fields["shops"].widget.choices = [(shop.pk, force_text(shop)) for shop in initial_shops]
        else:
            # drop shops fields
            self.fields.pop("shops", None)

        shop = get_shop(self.request)

        self.fields["is_approved"] = forms.BooleanField(
            label=_("Is approved for {}").format(shop),
            required=False,
            initial=True,
            help_text=_("Indicates whether this supplier is approved for the shop."),
        )
        for key, f in self.fields.items():
            print(key)
            if "description" in key:
                if configuration.get(None, SHUUP_ADMIN_ALLOW_HTML_IN_SUPPLIER_DESCRIPTION):
                    widget = TextEditorWidget()
                else:
                    widget = forms.Textarea(attrs={"rows": 5})
                self.fields[key].widget = widget
            if "content_header" in key:
                widget = forms.Textarea(attrs={"rows": 3})
                self.fields[key].widget = widget
            if "video_header" in key:
                widget = forms.Textarea(attrs={"rows": 3})
                self.fields[key].widget = widget
            if "desc" in key:
                if configuration.get(None, SHUUP_ADMIN_ALLOW_HTML_IN_SUPPLIER_DESCRIPTION):
                    widget = TextEditorWidget()
                else:
                    widget = forms.Textarea(attrs={"rows": 3})
                self.fields[key].widget = widget
        if self.instance.pk:
            supplier_shop = SupplierShop.objects.filter(shop=shop, supplier=self.instance).first()
            self.fields["is_approved"].initial = bool(supplier_shop and supplier_shop.is_approved)
        else:
            self.fields["is_approved"].initial = False

    def clean(self):
        cleaned_data = super(SupplierBaseForm, self).clean()
        stock_managed = cleaned_data.get("stock_managed")
        supplier_modules = cleaned_data.get("supplier_modules")

        if stock_managed and not supplier_modules:
            self.add_error("stock_managed", _("It is not possible to manage inventory when no module is selected."))

        if not configuration.get(None, SHUUP_ADMIN_ALLOW_HTML_IN_SUPPLIER_DESCRIPTION):
            for key, value in cleaned_data.items():
                if key.startswith("description__"):
                    cleaned_data[key] = bleach.clean(value, tags=[])

        if "shops" in self.fields:
            selected_shops = [int(shop_id) for shop_id in cleaned_data["shops"]]
            shop = get_shop(self.request)
            if cleaned_data.get("is_approved") and shop.pk not in selected_shops:
                self.add_error("is_approved", _("{} is not in the Shops field.").format(shop))

        return cleaned_data

    def save(self, commit=True):
        shop = get_shop(self.request)
        original_is_approved = None
        original_enabled = None

        if self.instance and self.instance.pk:
            original_enabled = Supplier.objects.only("enabled").get(pk=self.instance.pk).enabled
            supplier_shop = SupplierShop.objects.filter(shop=shop, supplier=self.instance).only("is_approved").first()
            if supplier_shop:
                original_is_approved = supplier_shop.is_approved

        instance = super(SupplierBaseForm, self).save(commit)
        instance.shop_products.remove(
            *list(instance.shop_products.exclude(shop_id__in=instance.shops.all()).values_list("pk", flat=True))
        )

        shop = get_shop(self.request)

        if not configuration.get(None, SHUUP_ENABLE_MULTIPLE_SUPPLIERS) or "shops" not in self.fields:
            instance.shops.add(shop)

        self._save_supplier_shop(shop, instance)

        should_reindex_products = False

        if "enabled" in self.cleaned_data:
            if original_enabled is not None and original_enabled != self.cleaned_data["enabled"]:
                should_reindex_products = True

        if "is_approved" in self.cleaned_data:
            if original_is_approved is not None and original_is_approved != self.cleaned_data["is_approved"]:
                should_reindex_products = True

        if should_reindex_products:
            supplier_products_reindex_required.send(sender=type(self), supplier=self.instance, shop=shop)

        return instance

    def _save_supplier_shop(self, shop, instance):
        # update the is_approved flag for this shop
        SupplierShop.objects.filter(shop=shop, supplier=instance).update(is_approved=self.cleaned_data["is_approved"])


class SupplierContactAddressForm(forms.ModelForm):
    class Meta:
        model = MutableAddress
        fields = (
            "name",
            "prefix",
            "suffix",
            "email",
            "phone",
            "tax_number",
            "street",
            "street2",
            "street3",
            "postal_code",
            "city",
            "region_code",
            "region",
            "country",
            "latitude",
            "longitude",
        )

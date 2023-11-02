# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.utils.translation import ugettext_lazy as _
from shuup.admin.forms.widgets import HexColorWidget
from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.core.models import Supplier

from givesome.enums import VendorExtraType
from givesome.models import GivesomePurse, PurchaseReportData, VendorExtra


class GivesomeVendorExtraForm(forms.Form):
    COLOR_CHOICES = (
        ('1', 'Type 1'),
        ('2', 'Type 2'),
        ('3', 'Type 3'),
    )
    vendor_type = forms.ChoiceField(
        help_text=_(
            "Indicates the type of vendor. "
            "WARNING! Changing this for existing vendors might lead to unexpected consequences."
        ),
        choices=VendorExtraType.choices(),
        required=True,
    )

    allow_brand_page = forms.BooleanField(
        label=_("Allow brand page"),
        help_text=_("Indicates whether this vendor is approved for a branded page."),
        required=False,
    )

    allow_purse = forms.BooleanField(
        label=_("Allow Brand Purse"),
        help_text=_(
            "Indicates whether this vendor is approved for a brand purse. "
            "If they are not, all funds are directed to Givesome's purse instead."
        ),
        required=False,
    )
    show_promoted = forms.BooleanField(
        label=_("Show promoted projects"),
        help_text=_("Show promoted projects"),
        required=False,
    )

    enable_receipting = forms.BooleanField(
        label=_("Enable Receipting"),
        help_text=_("Indicates whether this charity can issue receipts. Not applicable to brands."),
        required=False,
    )
    color = forms.CharField(
        required=False,
        label=_("Hex code for your organization's main colour."),
        help_text=_(
            "This code will tell the browser how to render your organization's colour on your brand page. A "
            "hex code is a hash symbol followed by six characters, which can be numbers 0-9 or the letters "
            "A-F."
        ),
        widget=HexColorWidget(),
    )

    website_url = forms.CharField(
        required=False,
        label=_("External website URL"),
        help_text=_("Enter the URL of the vendor's website"),
    )

    ordering = forms.IntegerField(
        required=False,
        label=_("Ordering"),
        help_text=_("This value is used for the ordering of vendors in lists. Higher ordering will be shown first"),
        initial=0,
    )

    sponsored_by = forms.ModelChoiceField(
        required=False,
        label=_("Sponsored by"),
        help_text=_("This vendor will be visible as this charity's sponsor on their brand page"),
        queryset=Supplier.objects.filter(deleted=False),
    )

    sponsor_link = forms.CharField(
        required=False,
        label=_("Sponsor website URL"),
        help_text=_("Sponsor link"),
    )
    display_type = forms.ChoiceField(
        help_text=_(
            "Display type"
        ),
        choices=COLOR_CHOICES,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            givesome_extra, __ = VendorExtra.objects.get_or_create(
                vendor=self.instance,
            )

            self.initial["allow_brand_page"] = givesome_extra.allow_brand_page
            self.fields["vendor_type"].initial = givesome_extra.vendor_type.value
            self.fields["ordering"].initial = givesome_extra.ordering
            self.fields["sponsored_by"].initial = givesome_extra.sponsored_by
            self.fields["allow_purse"].initial = givesome_extra.allow_purse
            self.fields["show_promoted"].initial = givesome_extra.show_promoted
            self.fields["enable_receipting"].initial = givesome_extra.enable_receipting
            self.fields["color"].initial = givesome_extra.color
            self.fields["website_url"].initial = givesome_extra.website_url
            self.fields["sponsor_link"].initial = givesome_extra.sponsor_link
            self.fields["display_type"].initial = givesome_extra.display_type

            if get_supplier(self.request):  # Disable/hide fields for suppliers
                self.fields["vendor_type"].disabled = True
                self.fields["allow_brand_page"].widget = HiddenInput()
                self.fields["allow_purse"].widget = HiddenInput()
                self.fields["show_promoted"].widget = HiddenInput()
                self.fields.pop("ordering", None)
                self.fields.pop("sponsored_by", None)
                self.fields.pop("enable_receipting", None)

            if givesome_extra.vendor_type == VendorExtraType.CHARITY:
                # Charities don't have a Brand Purse, as they cant have any Givecards in their name
                self.fields["allow_purse"].widget = HiddenInput()
                self.fields["show_promoted"].widget = HiddenInput()
                self.fields["registration_number"] = forms.CharField(
                    required=False,
                    label=_("Charity Registration Number"),
                    help_text=_("Enter the registration number"),
                )
                if givesome_extra.registration_number:
                    self.fields["registration_number"].initial = givesome_extra.registration_number

            if (  # Allow changing back to correct vendor type, if mixed up for some reason, otherwise disable
                givesome_extra.vendor_type == VendorExtraType.CHARITY
                and self.instance.shop_products.filter(product__deleted=False).exists()
            ) or (
                givesome_extra.vendor_type == VendorExtraType.BRANDED_VENDOR
                and PurchaseReportData.objects.filter(promoting_brand__id=self.instance.pk)
            ):
                self.fields["vendor_type"].disabled = True

        else:  # New vendor
            self.fields.pop("sponsored_by", None)

    def clean_website_url(self):
        website_url = self.cleaned_data["website_url"]
        if len(website_url) and not (website_url.startswith("http://") or website_url.startswith("https://")):
            raise ValidationError(_("Please make sure the link starts with `https://`"))
        return website_url

    def clean_sponsor_link(self):
        sponsor_link = self.cleaned_data["sponsor_link"]
        if len(sponsor_link) and not (sponsor_link.startswith("http://") or sponsor_link.startswith("https://")):
            raise ValidationError(_("Please make sure the link starts with `https://`"))
        return sponsor_link
    def clean_display_type(self):
        display_type = self.cleaned_data["display_type"]
        return display_type

    def clean_registration_number(self):
        registration = self.cleaned_data["registration_number"]
        return registration

    def save(self):
        if not self.has_changed():  # Nothing to do, don't bother iterating
            return
        givesome_extra, __ = VendorExtra.objects.get_or_create(vendor=self.instance)

        givesome_extra.color = self.cleaned_data.get("color")
        givesome_extra.website_url = self.cleaned_data.get("website_url")

        charity_registration = self.cleaned_data.get("registration_number")
        if charity_registration:
            givesome_extra.registration_number = charity_registration

        if not get_supplier(self.request):
            # Staff user has permission to make this change.
            givesome_extra.allow_brand_page = self.cleaned_data.get("allow_brand_page")
            givesome_extra.vendor_type = self.cleaned_data.get("vendor_type")
            givesome_extra.ordering = self.cleaned_data.get("ordering")
            givesome_extra.sponsored_by = self.cleaned_data.get("sponsored_by")
            givesome_extra.sponsor_link = self.cleaned_data.get("sponsor_link")
            givesome_extra.display_type = self.cleaned_data.get("display_type")
            givesome_extra.allow_purse = self.cleaned_data.get("allow_purse")
            givesome_extra.show_promoted = self.cleaned_data.get("show_promoted")
            givesome_extra.enable_receipting = self.cleaned_data.get("enable_receipting")
            GivesomePurse.objects.get_or_create(shop=get_shop(self.request), supplier=self.instance)
        givesome_extra.save()

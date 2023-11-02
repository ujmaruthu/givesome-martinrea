# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.forms import ModelChoiceField, ModelMultipleChoiceField
from shuup.admin.shop_provider import get_shop
from shuup.core.models import Supplier
from shuup.reports.forms import BaseReportForm

from givesome.enums import VendorExtraType
from givesome.models import GivecardCampaign, GivesomeOffice, GivesomePurse


class GivecardCampaignModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.identifier


class GivesomeBaseReportForm(BaseReportForm):
    filter_fields = ["brand_vendor", "offices" "charity", "campaign", "purse"]
    field_filter_choices = {
        "brand_vendor": ModelChoiceField(
            queryset=Supplier.objects.enabled().filter(
                givesome_extra__vendor_type=VendorExtraType.BRANDED_VENDOR, campaigns__isnull=False
            ),
            required=False,
        ),
        "offices": ModelMultipleChoiceField(
            queryset=GivesomeOffice.objects.filter(supplier__campaigns__isnull=False),
            required=False,
        ),
        "charity": ModelChoiceField(
            queryset=Supplier.objects.enabled().filter(
                givesome_extra__vendor_type=VendorExtraType.CHARITY, shop_products__isnull=False
            ),
            required=False,
        ),
        "campaign": GivecardCampaignModelChoiceField(
            queryset=GivecardCampaign.objects.filter(batches__isnull=False).distinct(),
            required=False,
        ),
        "purse": ModelChoiceField(
            queryset=GivesomePurse.objects.all(),
            required=False,
        ),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["shop"] = forms.CharField(initial=get_shop(self.request).id, widget=forms.HiddenInput())

        for field in self.filter_fields:
            if field in self.field_filter_choices:
                self.fields[field] = self.field_filter_choices[field]


class GivesomeGivecardReportForm(GivesomeBaseReportForm):
    filter_fields = ["brand_vendor", "offices", "charity", "campaign"]


class GivesomeCampaignReportForm(GivesomeBaseReportForm):
    filter_fields = ["campaign"]


class GivesomeBrandReportForm(GivesomeBaseReportForm):
    filter_fields = ["brand_vendor", "offices", "campaign"]


class GivesomePurseReportForm(GivesomeBaseReportForm):
    filter_fields = ["campaign", "purse"]

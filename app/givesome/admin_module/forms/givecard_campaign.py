# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.db.models import Count, Q
from django.forms import Select
from django.utils.translation import ugettext_lazy as _
from shuup.admin.forms import ShuupAdminForm
from shuup.core.models import Supplier

from givesome.enums import VendorExtraType
from givesome.models import GivecardCampaign, GivesomeGroup


class GivecardCampaignForm(ShuupAdminForm):
    class Meta:
        model = GivecardCampaign
        fields = ("identifier", "supplier", "image", "name", "message", "archived")
        labels = {
            "name": _("Campaign Name"),
            "message": _("Onboarding message"),
            "supplier": _("Branded Vendor"),
        }

    def __init__(self, **kwargs):
        """Restrict supplier choices to brand vendors"""
        self.request = kwargs.pop("request", None)
        super().__init__(**kwargs)
        qs = Supplier.objects.filter(
            enabled=True,
            givesome_extra__isnull=False,
            givesome_extra__vendor_type=VendorExtraType.BRANDED_VENDOR,
        )
        self.fields["supplier"].queryset = qs
        self.fields["identifier"].required = True

        # Allow selecting an existing Group, or entering a string to create a new one
        initial_group = None
        if self.instance.pk and self.instance.group:
            initial_group = self.instance.group.name
        group_choices = ((None, "---------"),) + tuple(GivesomeGroup.objects.values_list("name", "name"))

        self.fields["group"] = forms.CharField(
            required=False,
            label=_("Group"),
            help_text=_(
                "This is used to group Campaigns to different groups in the Vendor Dashboard, with their own subtotals."
            ),
            initial=initial_group,
            widget=Select(choices=group_choices, attrs={"data-select2-tags": "true"}),
        )

    def save(self, commit=False):
        if "group" in self.changed_data:
            # Remove old invalid groups
            GivesomeGroup.objects.annotate(count_campaigns=Count("campaigns")).filter(
                Q(count_campaigns=0) | Q(name="")
            ).delete()

            group_name = self.cleaned_data.get("group")
            group = None
            if group_name is not None and group_name != "":
                group, __ = GivesomeGroup.objects.get_or_create(name=group_name)
            self.instance.group = group
        return super().save(commit=True)

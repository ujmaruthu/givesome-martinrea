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
from django.utils.translation import ugettext_lazy as _
from shuup.admin.forms import ShuupAdminFormNoTranslation

from givesome.models import GivesomePurseAllocation


class GivesomePurseAllocationForm(ShuupAdminFormNoTranslation):
    class Meta:
        model = GivesomePurseAllocation
        fields = ("weight",)
        labels = {
            "weight": _("Weight"),
        }


class GivesomePurseManualDonateForm(ShuupAdminFormNoTranslation):
    class Meta:
        model = GivesomePurseAllocation
        fields = ()

    amount = forms.IntegerField(
        label=_("Manual donation amount"),
        help_text=_("Amount to donate from Givesome Purse"),
        required=True,
    )

    def clean_amount(self):
        """Donate at given sum or maximum amount possible"""
        amount = self.cleaned_data["amount"]
        max_donate_amount = self.instance.get_max_donate_amount()
        if max_donate_amount == 0:
            raise ValidationError(_("Not enough funds in Givesome Purse"))
        return min(amount, max_donate_amount)

    def save(self, **kwargs):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount > 0:
            self.instance.create_manual_donation(amount)
        return amount

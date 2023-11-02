# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.utils.translation import ugettext_lazy as _
from shuup import configuration
from shuup.admin.modules.settings.forms.system import BaseSettingsForm, BaseSettingsFormPart
from shuup.core.models import ConfigurationItem


def givesome_promote_invisible(shop):
    return configuration.get(shop, "givesome_allow_picking_invisible_projects", False)


def givesome_fully_funded_display_days(shop):
    return configuration.get(shop, "givesome_fully_funded_display_days", 3)


def get_donation_amount_options(shop):
    return (
        ConfigurationItem.objects.filter(shop=shop, key__contains="givesome_donation_amount_options")
        .annotate(value_int=Cast("value", IntegerField()))  # value is stored as a string
        .order_by("value_int")
    )


class GivesomeDonationAmountForm(forms.Form):

    amount = forms.IntegerField(min_value=1, label=_("A pre-determined amount a user may choose to donate."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "initial" in kwargs:
            self.fields["amount"].initial = kwargs["initial"].get("amount")


class GivesomeSettingsForm(BaseSettingsForm):
    title = _("Givesome Settings")

    givesome_allow_picking_invisible_projects = forms.BooleanField(
        label=_("Allow partner vendors to select invisible projects"),
        help_text=_(
            "Should Branded Vendors be able to pick a project, that is still invisible for customers, to be promoted"
            "on their brand page? It will be visible only after the charity changes it's visibility settings."
        ),
        required=False,
        initial=False,
    )

    givesome_fully_funded_display_days = forms.IntegerField(
        label=_("Days to display a project after being fully funded"),
        help_text=_("Days to display a project on the vendor pages after being fully funded."),
        required=True,
        initial=3,
    )


class GivesomeSettingsFormPart(BaseSettingsFormPart):
    form = GivesomeSettingsForm
    name = "givesome_settings"
    priority = 30

    def form_valid(self, form):
        form = form.forms[self.name]
        super().save(form)

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
from django.utils.translation import ugettext_lazy as _

from shuup.front.admin_module.forms import BaseSettingsForm, BaseSettingsFormPart


class RegistrationSettingsForm(BaseSettingsForm):
    title = _("Registration Settings")
    allow_company_registration = forms.BooleanField(
        label=_("Allow company registration"),
        help_text=_("If you select this, companies can register into your store."),
        required=False,
    )
    company_registration_requires_approval = forms.BooleanField(
        label=_("Company registration requires approval"),
        help_text=_(
            "Registered companies must be manually approved by admin if this is checked. "
            "This option has no effect if company registration is not allowed on your site."
        ),
        required=False,
    )
    validate_tax_number = forms.BooleanField(
        label=_("Company tax number validation"),
        help_text=_("Company tax number format is validated for European countries."),
        required=False,
    )


class RegistrationSettingsFormPart(BaseSettingsFormPart):
    form = RegistrationSettingsForm
    name = "registration_settings"
    priority = 9

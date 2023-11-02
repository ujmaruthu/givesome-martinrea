# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.utils.translation import ugettext_lazy as _

from shuup.admin.modules.settings.forms.system import BaseSettingsForm, BaseSettingsFormPart
from shuup.admin.utils.permissions import has_permission


class FrontSettingsForm(BaseSettingsForm):
    title = _("Front Settings")
    front_max_upload_size = forms.IntegerField(
        label=_("Front Max Upload Size"),
        help_text=_("Maximum allowed file size (in bytes) for uploads in frontend."),
        required=True,
    )
    registration_requires_activation = forms.BooleanField(
        label=_("Registration Requires Activation"),
        help_text=_(
            "Whether if a new user require email-based activate his account by clicking on a "
            "activation link sent by email."
        ),
        required=False,
    )
    customer_information_allow_picture_upload = forms.BooleanField(
        label=_("Customer Information Allow Picture Upload"),
        help_text=_("Allow customers to upload profile picture."),
        required=False,
    )


class FrontSettingsFormPart(BaseSettingsFormPart):
    form = FrontSettingsForm
    name = "front_settings"
    priority = 4

    def has_permission(self):
        return has_permission(self.request.user, "front.front_settings")

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


class ReportSettingsForm(BaseSettingsForm):
    title = _("Report Settings")
    default_reports_item_limit = forms.IntegerField(
        label=_("Default Report Item Limit"),
        help_text=_("Defines the maximum number of items that will be rendered by a report."),
        required=True,
    )


class ReportSettingsFormPart(BaseSettingsFormPart):
    form = ReportSettingsForm
    name = "report_settings"
    priority = 5

    def has_permission(self):
        return has_permission(self.request.user, "reports.report_settings")

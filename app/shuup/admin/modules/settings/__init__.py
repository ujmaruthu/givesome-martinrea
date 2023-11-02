# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import SETTINGS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url


class SettingsModule(AdminModule):
    name = _("System Settings")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:settings.list")

    def get_urls(self):
        return [admin_url("^settings/$", "shuup.admin.modules.settings.views.SystemSettingsView", name="settings.list")]

    def get_extra_permissions(self):
        return [
            "system_settings.admin_settings",
            "system_settings.core_settings",
            "system_settings.order_settings",
        ]

    def get_permissions_help_texts(self):
        return {
            "system_settings.admin_settings": _("Whether the user can configure the Admin Settings"),
            "system_settings.core_settings": _("Whether the user can configure the Core Settings"),
            "system_settings.order_settings": _("Whether the user can configure the Order Settings"),
        }

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-home",
                url="shuup_admin:settings.list",
                category=SETTINGS_MENU_CATEGORY,
                ordering=4,
            )
        ]

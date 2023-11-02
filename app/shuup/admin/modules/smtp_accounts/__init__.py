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
from shuup.admin.utils.urls import admin_url, derive_model_url, get_edit_and_list_urls
from shuup.core.models import SMTPAccount


class SMTPAccountModule(AdminModule):
    name = _("SMTP Accounts")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:smtp_account.list")

    def get_urls(self):
        return get_edit_and_list_urls(
            url_prefix="^smtp_accounts",
            view_template="shuup.admin.modules.smtp_accounts.views.SMTPAccount%sView",
            name_template="smtp_account.%s",
        ) + [
            admin_url(
                r"^smtp_accounts/(?P<pk>\d+)/delete/$",
                "shuup.admin.modules.smtp_accounts.views.SMTPAccountDeleteView",
                name="smtp_account.delete",
            ),
        ]

    def get_menu_category_icons(self):
        return {self.name: "fa fa-envelope-o"}

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("SMTP Accounts"),
                icon="fa fa-envelope-o",
                url="shuup_admin:smtp_account.list",
                category=SETTINGS_MENU_CATEGORY,
                ordering=500,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(SMTPAccount, "shuup_admin:smtp_account", object, kind)

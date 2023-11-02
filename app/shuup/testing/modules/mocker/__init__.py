# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import SETTINGS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url


class TestingAdminModule(AdminModule):
    def get_urls(self):
        return [admin_url("^mocker/$", "shuup.testing.modules.mocker.mocker_view.MockerView", name="mocker")]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text="Create Mock Objects", category=SETTINGS_MENU_CATEGORY, url="shuup_admin:mocker", icon="fa fa-star"
            )
        ]

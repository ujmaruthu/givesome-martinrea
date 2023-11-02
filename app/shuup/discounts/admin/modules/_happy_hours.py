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
from shuup.admin.menu import CAMPAIGNS_MENU_CATEGORY
from shuup.admin.utils.urls import derive_model_url, get_edit_and_list_urls
from shuup.discounts.models import HappyHour


class HappyHourModule(AdminModule):
    name = _("Discounts Happy Hours")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:discounts_happy_hour.list")

    def get_urls(self):
        from shuup.admin.urls import admin_url

        delete = admin_url(
            r"^discounts_happy_hour/(?P<pk>\d+)/delete/$",
            "shuup.discounts.admin.views.HappyHourDeleteView",
            name="discounts_happy_hour.delete",
        )

        return [delete] + get_edit_and_list_urls(
            url_prefix="^discounts_happy_hour",
            view_template="shuup.discounts.admin.views.HappyHour%sView",
            name_template="discounts_happy_hour.%s",
        )

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Product Discounts Happy Hours"),
                icon="fa fa-percent",
                url="shuup_admin:discounts_happy_hour.list",
                category=CAMPAIGNS_MENU_CATEGORY,
                ordering=7,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(HappyHour, "shuup_admin:discounts_happy_hour", object, kind)

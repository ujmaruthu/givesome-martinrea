# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import Column, TextFilter, true_or_false_filter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import SMTPAccount


class SMTPAccountListView(PicotableListView):
    model = SMTPAccount

    default_columns = [
        Column(
            "name",
            _("Account Name"),
            sort_field="rname",
            display="name",
            filter_config=TextFilter(filter_field="name", placeholder=_("Filter by account name...")),
            ordering=1,
        ),
        Column(
            "host",
            _("Host"),
            display="host",
            filter_config=TextFilter(filter_field="host", placeholder=_("Filter by host name...")),
            ordering=2,
        ),
        Column(
            "shop",
            _("Shop"),
            display="shop__name",
            filter_config=TextFilter(filter_field="shop__name", placeholder=_("Filter by name...")),
            ordering=3,
        ),
        Column(
            "default_account",
            _("Is Default Account"),
            display="default_account",
            filter_config=true_or_false_filter,
            ordering=4,
        ),
    ]

    related_objects = [
        ("shop", "shuup.core.models:Shop"),
    ]

    toolbar_buttons_provider_key = "smtp_account_list_toolbar_provider"
    mass_actions_provider_key = "smtp_account_list_mass_actions_provider"

    def get_queryset(self):
        return SMTPAccount.objects.filter(Q(shop__isnull=True) | Q(shop=get_shop(self.request)))

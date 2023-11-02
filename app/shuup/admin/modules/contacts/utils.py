# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.exceptions import PermissionDenied

from shuup import configuration
from shuup.admin.shop_provider import get_shop
from shuup.core.setting_keys import SHUUP_ENABLE_MULTIPLE_SHOPS, SHUUP_MANAGE_CONTACTS_PER_SHOP


def request_limited(request):
    return (
        configuration.get(None, SHUUP_ENABLE_MULTIPLE_SHOPS)
        and configuration.get(None, SHUUP_MANAGE_CONTACTS_PER_SHOP)
        and not request.user.is_superuser
    )


def check_contact_permission(request, contact):
    shop = get_shop(request)
    if request_limited(request) and not contact.in_shop(shop):
        raise PermissionDenied()

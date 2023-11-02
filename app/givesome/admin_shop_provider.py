# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import Shop

SHOP_SESSION_KEY = "admin_shop"


class AdminShopProvider(object):
    def get_shop(self, request):
        if not request.user.is_staff:
            return None

        return Shop.objects.first()

    def set_shop(self, request, shop=None):
        if not request.user.is_staff:
            raise PermissionDenied(_("You must have the Access to Admin Panel permission."))

        if shop:
            # only can set if the user is superuser or is the shop staff
            if shop.staff_members.filter(pk=request.user.pk).exists() or request.user.is_superuser:
                request.session[SHOP_SESSION_KEY] = shop.id
            else:
                raise PermissionDenied(_("You must have the Access to Admin Panel permissions to this shop."))

        else:
            self.unset_shop(request)

    def unset_shop(self, request):
        if SHOP_SESSION_KEY in request.session:
            del request.session[SHOP_SESSION_KEY]

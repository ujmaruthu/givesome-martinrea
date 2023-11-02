# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.admin.shop_provider import get_shop


class MultivendorSupplierProvider(object):
    @classmethod
    def get_supplier(cls, request, **kwargs):
        # TODO: change to make it possible to user select the supplier when more than 1 is available
        # return the first linked enabled supplier
        if hasattr(request.user, "vendor_users"):
            vendor_user = request.user.vendor_users.filter(
                supplier__enabled=True, supplier__deleted=False, user__is_active=True, shop=get_shop(request)
            ).first()
            if vendor_user:
                return vendor_user.supplier

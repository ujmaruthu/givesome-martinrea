# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.core.models import Shop


class DefaultShopProvider(object):
    @classmethod
    def get_shop(cls, request, **kwargs):
        shop = getattr(request, "_cached_default_shop_provider_shop", None)
        if shop:
            return shop

        shop = Shop.objects.first()
        # cache shop as we already calculated it
        setattr(request, "_cached_default_shop_provider_shop", shop)
        return shop

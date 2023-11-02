# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.


class FirstSupplierStrategy(object):
    def get_supplier(self, **kwargs):
        shop_product = kwargs["shop_product"]
        return shop_product.suppliers.enabled(shop=shop_product.shop).first()

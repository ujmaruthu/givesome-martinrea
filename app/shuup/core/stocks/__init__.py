# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.core.utils.product_caching_object import ProductCachingObject


class ProductStockStatus(ProductCachingObject):
    logical_count = 0
    physical_count = 0
    message = None
    error = None
    stock_managed = False
    # when the supplier module handles the product
    handled = False

    def __init__(
        self,
        product=None,
        product_id=None,
        logical_count=0,
        physical_count=0,
        message=None,
        error=None,
        stock_managed=False,
        handled=True,
        *args,
        **kwargs
    ):
        if product_id:
            self.product_id = product_id
        else:
            self.product = product
        if not self.product_id:
            raise ValueError("Error! `ProductStockStatus` object must be bound to Products.")
        self.logical_count = logical_count
        self.physical_count = physical_count
        self.message = message
        self.error = error
        self.stock_managed = stock_managed
        self.handled = handled

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from typing import Iterable

from shuup.admin.modules.products.issues import ProductValidationIssue
from shuup.core.models import Shop, ShopProduct, Supplier


class AdminProductValidator:
    """Base class for validating products."""

    ordering = 0

    def get_validation_issues(
        shop_product: ShopProduct, shop: Shop, user, supplier: Supplier = None
    ) -> Iterable[ProductValidationIssue]:
        yield None

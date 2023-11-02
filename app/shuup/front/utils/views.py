# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import with_statement

from django.utils.translation import get_language

from shuup.core.models import Product, ProductAttribute
from shuup.utils.translation import cache_translations


def cache_product_things(request, products, language=None, attribute_identifiers=[]):
    # Cache necessary things for products. WARNING: This will cause queryset iteration.
    language = language or get_language()
    if attribute_identifiers:
        Product.cache_attributes_for_targets(
            ProductAttribute, products, attribute_identifiers=attribute_identifiers, language=language
        )
    products = cache_translations(products, (language,))
    return products

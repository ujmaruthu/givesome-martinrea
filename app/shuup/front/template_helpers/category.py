# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import get_language
from jinja2.utils import contextfunction

from shuup.core.models import Manufacturer


@contextfunction
def get_manufacturers(context):
    request = context["request"]
    category = context["category"]
    manufacturers_ids = (
        category.products.all_visible(request, language=get_language()).values_list("manufacturer__id").distinct()
    )
    return Manufacturer.objects.filter(pk__in=manufacturers_ids)

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.db.models import Case, When


def order_query_by_values(queryset, values):
    order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(values)])
    if values:
        queryset = queryset.order_by(order)
    return queryset

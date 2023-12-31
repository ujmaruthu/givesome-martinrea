# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from collections import OrderedDict
from django.db import connection

from shuup.utils.dates import parse_date


def group_by_period(queryset, column, period, **annotate):
    """
    Group and annotate given queryset by a given date period.

    :param queryset: Original queryset
    :type queryset: django.db.QuerySet
    :param column: Column for grouping
    :type column: str
    :param period: Period for grouping ('year', 'month', 'day')
    :type period:  str
    :param annotate: Dict for `.annotate()`
    :type annotate: dict[str,str]
    :return: OrderedDict of period -> annotate columns
    :rtype: collections.OrderedDict
    """

    # Based on http://stackoverflow.com/a/8746532/51685

    d = OrderedDict()
    for line in (
        queryset.extra({"period_group": connection.ops.date_trunc_sql(period, column)})
        .values("period_group")
        .annotate(**annotate)
        .order_by("period_group")
        .values(*["period_group"] + list(annotate.keys()))
    ):
        d[parse_date(line.pop("period_group"))] = line
    return d

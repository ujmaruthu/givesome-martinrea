# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db.models import Count, IntegerField, Subquery, Sum
from django.db.models.functions import Coalesce
from shuup.admin.utils.picotable import ChoicesFilter


class HasValueFilter(ChoicesFilter):
    def __init__(self, choices=None, filter_field=None, default=None, labels={"true": "yes", "false": "no"}):
        super().__init__(choices, filter_field, default)
        self.choices = [(True, labels["false"]), (False, labels["true"])]

    def filter_queryset(self, queryset, column, value, context):
        if value == "_all":
            return queryset
        filter_field = f"{self.get_filter_field(column, context)}__isnull"
        return queryset.filter(**{filter_field: value})


class BoolFilter(ChoicesFilter):
    def __init__(self, choices=None, filter_field=None, default=None):
        super().__init__(choices, filter_field, default)
        self.choices = [(True, "yes"), (False, "no")]


def CoalesceZero(queryset):
    return Coalesce(queryset, 0)


class DistinctSum(Sum):
    template = "%(function)s(DISTINCT %(expressions)s)"


class DistinctCount(Count):
    template = "%(function)s(DISTINCT %(expressions)s)"


class SQCount(Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()


class SQSum(Subquery):
    """Refs. (https://stackoverflow.com/a/58001368)"""

    template = "(SELECT SUM(%(sum_field)s) FROM (%(subquery)s) _sum)"
    output_field = IntegerField()

    def __init__(self, queryset, output_field=None, *, sum_field="", **extra):
        extra["sum_field"] = sum_field
        super().__init__(queryset, output_field, **extra)

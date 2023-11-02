# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db.models import Exists, OuterRef
from shuup.front.forms.product_list_modifiers import SimpleProductListModifier

from givesome.models import ProjectExtra


class AvailableProductListFilter(SimpleProductListModifier):
    def should_use(self, configuration):
        return True

    def get_ordering(self, configuration):
        return 0

    def get_fields(self, request, category=None):
        return []

    def get_queryset(self, queryset, data):
        """
        Exclude projects that became too long ago
        And those which don't have ProjectExtra object attached which are invalid anyway
        """
        listed_products = ProjectExtra.objects.listed().filter(project=OuterRef("pk"))
        return queryset.annotate(is_listed=Exists(listed_products)).filter(is_listed=True)

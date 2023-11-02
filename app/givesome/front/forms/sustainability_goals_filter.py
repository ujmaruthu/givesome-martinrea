# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from shuup.core.utils import context_cache
from shuup.front.forms.product_list_modifiers import CommaSeparatedListField, FilterWidget, SimpleProductListModifier

from givesome.models import SustainabilityGoal


class SustainabilityGoalsProjectListFilter(SimpleProductListModifier):
    is_active_key = "filter_projects_by_sustainability_goal"
    is_active_label = _("Filter projects by Sustainable Development Goal")
    ordering_key = "filter_projects_by_sustainability_goal_ordering"
    ordering_label = _("Ordering for projects by Sustainable Development Goal")

    def get_fields(self, request, category=None):
        key, val = context_cache.get_cached_value(
            identifier="sustainabilitygoalproductfilter", item=self, context=request, category=category
        )
        if val:
            return val

        queryset = SustainabilityGoal.objects.all()
        data = [
            (
                "sustainability_goals",
                CommaSeparatedListField(
                    required=False,
                    label=_("Sustainable Development Goals"),
                    widget=FilterWidget(choices=[(sdg.pk, sdg.name) for sdg in queryset]),
                ),
            )
        ]
        context_cache.set_cached_value(key, data)
        return data

    def get_filters(self, request, data):
        sdg_ids = data.get("sustainability_goals")
        if not sdg_ids:
            return

        if not isinstance(sdg_ids, (list, tuple)):
            sdg_ids = list(sdg_ids)

        sdg_ids = [sdg.strip() for sdg in sdg_ids if sdg]
        if sdg_ids:
            return Q(
                shop_products__project_sustainability_goals__goals__in=SustainabilityGoal.objects.filter(pk__in=sdg_ids)
            )

    def get_admin_fields(self):
        default_fields = super(SustainabilityGoalsProjectListFilter, self).get_admin_fields()
        default_fields[0][1].help_text = _(
            "Enable this to allow projects to be filterable by Sustainable Development Goals "
        )
        default_fields[1][1].help_text = _(
            "Use a numeric value to set the order in which the Sustainability Goal list filters will appear on the "
            "product listing page."
        )
        return default_fields

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.views.generic.base import TemplateView
from shuup.admin.supplier_provider import get_supplier

from givesome.admin_module.dashboard.blocks import (
    get_campaign_table_block,
    get_continued_giving_blocks,
    get_lives_impacted_block,
    get_percentage_givecards_redeemed_block,
    get_projects_funded_block,
    get_total_donated_block,
)
from givesome.enums import VendorExtraType
from givesome.models import GivecardCampaign


class GivesomeSupplierDashboardView(TemplateView):
    template_name = "shuup_multivendor/admin/dashboard/dashboard.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        supplier = get_supplier(request)
        campaigns = None
        campaign_groups = [(None, None)]
        context["blocks"] = {}

        # Brand vendor dashboard
        if supplier and supplier.givesome_extra.vendor_type == VendorExtraType.BRANDED_VENDOR:
            campaigns = GivecardCampaign.objects.filter(
                supplier=supplier,
                archived=False,
            ).distinct()
            campaign_groups = campaigns.values_list("group_id", "group__name")

        if campaigns:
            if len(campaign_groups) > 1:
                context["blocks"]["ALL_CAMPAIGNS"] = [
                    # Total of all Campaigns
                    get_percentage_givecards_redeemed_block(campaigns=campaigns, group_name="ALL_CAMPAIGNS"),
                    get_total_donated_block(campaigns=campaigns, group_name="ALL_CAMPAIGNS"),
                    get_projects_funded_block(campaigns=campaigns, group_name="ALL_CAMPAIGNS"),
                    get_lives_impacted_block(campaigns=campaigns, group_name="ALL_CAMPAIGNS"),
                    *get_continued_giving_blocks(campaigns=campaigns, group_name="ALL_CAMPAIGNS"),
                ]

            for group_id, group_name in campaign_groups:
                group_campaigns = campaigns.filter(group=group_id)
                context["blocks"][group_name] = [
                    # Top row blocks
                    get_percentage_givecards_redeemed_block(campaigns=group_campaigns, group_name=group_name),
                    get_total_donated_block(campaigns=group_campaigns, group_name=group_name),
                    get_projects_funded_block(campaigns=group_campaigns, group_name=group_name),
                    get_lives_impacted_block(campaigns=group_campaigns, group_name=group_name),
                    *get_continued_giving_blocks(campaigns=group_campaigns, group_name=group_name),
                    # Campaigns Table
                    get_campaign_table_block(request=request, campaigns=group_campaigns, group_name=group_name),
                ]

        return context

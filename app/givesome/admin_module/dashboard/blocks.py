# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from typing import Union

from babel.numbers import format_number
from django.utils.translation import ugettext_lazy as _
from shuup.admin.dashboard import DashboardContentBlock, DashboardNumberBlock, DashboardValueBlock
from shuup.utils.i18n import get_current_babel_locale
from shuup.utils.numbers import parse_decimal_string


class GivesomeMoneyBlock(DashboardValueBlock):
    """Parse value like a DashboardNumberBlock, but add a $ prefix to the value"""

    def __init__(self, id, value, title, **kwargs):
        value = parse_decimal_string(value)
        if int(value) == value:
            value = int(value)
        value = format_number(value, locale=get_current_babel_locale())
        super().__init__(id, f"$ {value}", title, **kwargs)


def easy_block(block_class, id: str, color: str, title: str, value: Union[str, int], group_name: str, *args, **kwargs):
    total_all_campaigns = group_name == "ALL_CAMPAIGNS"
    return block_class(
        id=f"{id}_{group_name}",
        color=total_all_campaigns and "purple" or color,
        title=total_all_campaigns and (_("Total %(block_title)s") % {"block_title": title}) or title,
        value=value,
        *args,
        **kwargs,
    )


def get_percentage_givecards_redeemed_block(campaigns, group_name):
    value = campaigns.aggregate_givecards_redeemed(hide_archived_batches=True)
    value = f"{round(value)}%"
    return easy_block(DashboardValueBlock, "givecards_redeemed", "green", _("Cards Redeemed"), value, group_name)


def get_total_donated_block(campaigns, group_name):
    value = campaigns.aggregate_total_amount_donated(hide_archived_batches=True)
    return easy_block(GivesomeMoneyBlock, "total_donated", "yellow", _("Amount Donated"), value, group_name)


def get_projects_funded_block(campaigns, group_name):
    value = campaigns.aggregate_count_projects_donated(hide_archived_batches=True)
    return easy_block(DashboardNumberBlock, "projects_funded", "blue", _("Projects Funded") + " *", value, group_name)


def get_lives_impacted_block(campaigns, group_name):
    value = campaigns.aggregate_sum_lives_impacted(hide_archived_batches=True)
    return easy_block(DashboardNumberBlock, "lives_impacted", "red", _("Lives Impacted") + " *", value, group_name)


def get_continued_giving_blocks(campaigns, group_name):
    values = campaigns.aggregate_continued_giving(hide_archived_batches=True)
    blocks = [
        easy_block(
            DashboardNumberBlock,
            "continued_givers",
            "green",
            _("Continued Givers"),
            values["continued_givers"],
            group_name,
        ),
        easy_block(
            GivesomeMoneyBlock,
            "continued_giving",
            "yellow",
            _("Continued Giving"),
            values["continued_giving"],
            group_name,
        ),
        easy_block(
            GivesomeMoneyBlock,
            "off_platform_donated",
            "blue",
            _("Off-Platform Donations"),
            values["off_platform_donated"],
            group_name,
        ),
        easy_block(
            DashboardNumberBlock,
            "off_platform_hours",
            "red",
            _("Volunteer hours"),
            values["off_platform_hours"],
            group_name,
        ),
    ]
    return blocks


def _get_campaign_data_for_table(campaigns):
    return (
        campaigns.annotate_percentage_redeemed(hide_archived_batches=True)
        .annotate_count_projects_donated(hide_archived_batches=True)
        .annotate_total_amount_donated(hide_archived_batches=True)
        .annotate_continued_giving(hide_archived_batches=True)
        .order_by("-percentage_redeemed")
    )


def get_campaign_table_block(request, campaigns, group_name: str):
    if group_name is None:
        group_name = _("By Givecard Campaign")
    block = DashboardContentBlock.by_rendering_template(
        "campaign_table",
        request,
        "givesome/admin/dashboard/givecard_campaigns_block.jinja",
        {
            "title": group_name,
            "campaigns": _get_campaign_data_for_table(campaigns=campaigns),
        },
    )
    block.size = "full"
    return block

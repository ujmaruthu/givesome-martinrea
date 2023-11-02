# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import Payment
from shuup.reports.report import ShuupReportBase

from givesome.admin_module.reports.forms import GivesomeBrandReportForm
from givesome.admin_module.reports.utils import GivecardMixin, GivesomeOrderMixin
from givesome.models import Givecard, GivecardCampaign, ProjectExtra, PurchaseReportData


class CampaignSummaryReport(GivesomeOrderMixin, GivecardMixin, ShuupReportBase):
    identifier = "campaign_summary_report"
    title = _("Givesome Campaign Summary Report")
    filename_template = "campaign_summary-report-%(time)s"
    form_class = GivesomeBrandReportForm

    schema = [
        {"key": "brand", "title": _("Brand")},
        {"key": "campaign_name", "title": _("Campaign")},
        {"key": "redeemed", "title": _("Cards redeemed")},
        {"key": "donations_count", "title": _("Donations made")},
        {"key": "donations_value", "title": _("Total donated")},
        {"key": "projects_count", "title": _("Projects")},
        {"key": "lives_impacted", "title": _("Lives impacted")},
        {"key": "continued_givers", "title": _("Continued Givers")},
    ]

    def get_data(self):
        data = []
        orders = self.get_charity_order_objects()
        campaigns = self.get_campaign_objects().annotate_percentage_redeemed()
        for campaign in campaigns:
            givecards = Givecard.objects.filter(
                batch__campaign=campaign
            )  # All Givecards in Campaign
            order_payments = Payment.objects.filter(order__in=orders)
            purchase_report_data = PurchaseReportData.objects.filter(
                givecard__in=givecards, payment__in=order_payments
            )
            projects = set(
                purchase_report_data.values_list("project", flat=True)
            )  # Unique projects donated to

            donations_count = orders.filter(
                payments__purchase_report_data__givecard__in=givecards
            ).count()
            donations_value = (
                purchase_report_data.aggregate(
                    sum_donated=Sum("payment__amount_value")
                )["sum_donated"]
                or 0
            )

            if donations_count == 0:
                continue

            projects_count = len(projects)
            lives_impacted = (
                ProjectExtra.objects.filter(project_id__in=projects).aggregate(
                    lives=Sum("lives_impacted")
                )["lives"]
                or 0
            )
            continued_givers = GivecardCampaign.objects.filter(
                pk=campaign.pk
            ).aggregate_continued_giving(hide_archived_batches=True)["continued_givers"]

            data.append(
                {
                    "brand": campaign.supplier if campaign.supplier is not None else "",
                    "campaign_name": campaign.name,
                    "redeemed": f"{campaign.sum_redeemed_givecards} / {campaign.sum_givecards} "
                    f"({ campaign.percentage_redeemed }%)",
                    "donations_count": donations_count,
                    "donations_value": donations_value,
                    "projects_count": projects_count,
                    "lives_impacted": lives_impacted,
                    "continued_givers": continued_givers,
                }
            )
        return self.get_return_data(data, has_totals=False)

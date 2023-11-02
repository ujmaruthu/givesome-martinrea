# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.utils.translation import ugettext_lazy as _
from shuup.reports.report import ShuupReportBase
from shuup.utils.i18n import get_locally_formatted_datetime

from givesome.admin_module.reports.forms import GivesomeCampaignReportForm
from givesome.admin_module.reports.utils import GivecardMixin, GivesomeOrderMixin, GivesomePurseMixin


class AllAutomaticDonationsReport(GivesomeOrderMixin, GivesomePurseMixin, GivecardMixin, ShuupReportBase):
    identifier = "givesome_automatic_donations_report"
    title = _("Givesome Automatic Donations Donations Report")
    filename_template = "givesome-automatic-donations-report-%(time)s"
    form_class = GivesomeCampaignReportForm

    schema = [
        {"key": "project", "title": _("Project")},
        {"key": "campaign", "title": _("Campaign")},
        {"key": "donation_type", "title": _("Donation Type")},
        {"key": "donor", "title": _("Donor")},
        {"key": "donated_amount", "title": _("Amount")},
        {"key": "order_date", "title": _("Donation Date")},
    ]

    def get_data(self):
        data = []
        donations = self.get_automatic_donation_data_objects()
        for donation in donations:
            data.append(
                {
                    "project": donation.get_project(),
                    "campaign": donation.batch.campaign.name if donation.batch.campaign is not None else "",
                    "donation_type": donation.donation_type,
                    "donor": donation.get_donor(),
                    "donated_amount": donation.payment.amount_value,
                    "order_date": get_locally_formatted_datetime(donation.payment.order.order_date),
                }
            )
        return self.get_return_data(data, has_totals=False)

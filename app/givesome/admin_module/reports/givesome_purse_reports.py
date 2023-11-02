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

from givesome.admin_module.reports.forms import GivesomePurseReportForm
from givesome.admin_module.reports.utils import GivesomeOrderMixin, GivesomePurseMixin


class GivesomePurseChargeReport(GivesomePurseMixin, ShuupReportBase):
    identifier = "givesome_purse_charge_report"
    title = _("Givesome Purse Charge Report")
    filename_template = "givesome-purse-charge-report-%(time)s"
    form_class = GivesomePurseReportForm

    schema = [
        {"key": "purse", "title": _("Purse")},
        {"key": "campaign", "title": _("Campaign")},
        {"key": "batch", "title": _("Batch")},
        {"key": "charge_amount", "title": _("Amount")},
        {"key": "charge_date", "title": _("Charge Date")},
    ]

    def get_data(self):
        data = []
        total = 0
        for charge in self.get_purse_charge_objects():
            data.append(
                {
                    "purse": charge.purse.name,
                    "campaign": charge.batch.campaign.name if charge.batch.campaign is not None else "",
                    "batch": charge.batch,
                    "charge_amount": charge.charge_amount,
                    "charge_date": get_locally_formatted_datetime(charge.charge_date),
                }
            )
            total += charge.charge_amount
        data.append(
            {
                "purse": "",
                "campaign": "",
                "batch": _("Total charges:"),
                "charge_amount": total,
                "charge_date": "",
            }
        )
        return self.get_return_data(data, has_totals=False)


class GivesomePurseManualDonateReport(GivesomeOrderMixin, GivesomePurseMixin, ShuupReportBase):
    identifier = "givesome_purse_donations"
    title = _("Givesome Purse Donations Report")
    filename_template = "givesome-purse-donations-report-%(time)s"
    form_class = GivesomePurseReportForm

    schema = [
        {"key": "project", "title": _("Project")},
        {"key": "donation_amount", "title": _("Amount")},
        {"key": "donation_date", "title": _("Donation date")},
    ]

    def get_data(self):
        data = []
        total = 0
        donations = self.get_manual_donation_data_objects()
        for donation in donations:
            data.append(
                {
                    "project": donation.get_project(),
                    "donation_amount": donation.payment.amount_value,
                    "donation_date": get_locally_formatted_datetime(donation.payment.order.order_date),
                }
            )
            total += donation.payment.amount_value.charge_amount
        data.append(
            {
                "project": _("Total charges:"),
                "donation_amount": total,
                "donation_date": "",
            }
        )
        return self.get_return_data(data, has_totals=False)

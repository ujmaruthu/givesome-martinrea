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

from givesome.admin_module.reports.forms import GivesomeBrandReportForm, GivesomeGivecardReportForm
from givesome.admin_module.reports.utils import GivecardMixin, GivesomeOrderMixin


class GivecardDonationReport(GivesomeOrderMixin, GivecardMixin, ShuupReportBase):
    identifier = "givecard_donation_report"
    title = _("Givecard Donation Report")
    filename_template = "givecard-donation-report-%(time)s"
    form_class = GivesomeGivecardReportForm

    schema = [
        {"key": "code", "title": _("Givecard")},
        {"key": "campaign", "title": _("Campaign")},
        {"key": "promoting_brand", "title": _("Brand")},
        {"key": "promoting_office", "title": _("Office")},
        {"key": "project", "title": _("Project")},
        {"key": "donated_amount", "title": _("Amount")},
        {"key": "order_date", "title": _("Order Date")},
        {"key": "user", "title": _("User")},
    ]

    def get_data(self):
        data = []
        for purchase in self.get_givecard_purchase_data_objects():
            data.append(
                {
                    "code": purchase.givecard.get_code(),
                    "campaign": purchase.givecard.batch.campaign.identifier,
                    "promoting_brand": purchase.get_brand_name(),
                    "promoting_office": purchase.get_office_name(),
                    "project": purchase.project,
                    "donated_amount": int(purchase.payment.amount_value),  # Always full dollar amounts
                    "order_date": get_locally_formatted_datetime(purchase.payment.order.order_date),
                    "user": purchase.payment.order.get_customer_name(),
                }
            )
        return self.get_return_data(data, has_totals=False)


class GivecardRedemptionReport(GivecardMixin, ShuupReportBase):
    identifier = "givecard_redemption_report"
    title = _("Givecard Redemption Report")
    filename_template = "givecard-redemption-report-%(time)s"
    form_class = GivesomeBrandReportForm

    schema = [
        {"key": "code", "title": _("Givecard")},
        {"key": "campaign", "title": _("Campaign")},
        {"key": "amount", "title": _("Amount")},
        {"key": "redemption_date", "title": _("Redeemed Date")},
        {"key": "user", "title": _("User")},
        {"key": "brand_vendor", "title": _("Brand Vendor")},
        {"key": "office", "title": _("Office")},
    ]

    def get_data(self):
        data = []
        for givecard in self.get_redeemed_givecard_objects():
            data.append(
                {
                    "code": givecard.get_code(),
                    "campaign": givecard.batch.campaign.identifier,
                    "amount": givecard.batch.value,
                    "redemption_date": get_locally_formatted_datetime(givecard.redeemed_on),
                    "user": givecard.user.contact if givecard.user is not None else "Anonymous",
                    "brand_vendor": givecard.batch.supplier.name if givecard.batch.supplier is not None else "",
                    "office": givecard.batch.office.name if givecard.batch.office is not None else "",
                }
            )
        return self.get_return_data(data, has_totals=False)

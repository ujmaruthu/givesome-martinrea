# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from decimal import Decimal

from django.forms import ChoiceField
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import OrderLine, OrderLineType, Supplier
from shuup.default_reports.reports import OrderLineReport
from shuup.reports.forms import BaseReportForm
from shuup.utils.dates import to_datetime_range
from shuup_stripe_multivendor.models import StripeMultivendorPaymentProcessor

from givesome.enums import VendorExtraType


class ReceiptingBaseReportForm(BaseReportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["charity"] = ChoiceField(
            label=_("Charity"),
            help_text=_("Filter report results by charity."),
            choices=[
                (charity.pk, charity.name)
                for charity in Supplier.objects.filter(givesome_extra__vendor_type=VendorExtraType.CHARITY)
            ],
        )


class ReceiptingReport(OrderLineReport):
    """Create a report for all Stripe donations for end-of-year receipting purposes."""

    identifier = "receipting_report"
    title = _("Receipting Report")
    filename_template = "receipting-report-%(time)s"
    form_class = ReceiptingBaseReportForm
    schema = [
        {"key": "name", "title": _("Donor name")},
        {"key": "email", "title": _("Donor email")},
        {"key": "original_donation_amount", "title": _("Original donation amount")},
        {"key": "donation_amount", "title": _("Donation amount")},
        {"key": "project_name", "title": _("Project name")},
        {"key": "charity_name", "title": _("Charity name")},
        {"key": "addr_street", "title": _("Donor Street")},
        {"key": "addr_street2", "title": _("Donor Street (2)")},
        {"key": "addr_street3", "title": _("Donor Street (3)")},
        {"key": "addr_code", "title": _("Donor Postal Code")},
        {"key": "addr_city", "title": _("Donor City")},
        {"key": "addr_region", "title": _("Donor Region")},
        {"key": "addr_country", "title": _("Donor Country")},
    ]

    def __init__(self, **kwargs):
        charity_pk = kwargs.pop("charity", None)
        if charity_pk:
            self.charity = Supplier.objects.filter(id=charity_pk).first()
        super().__init__(**kwargs)

    def get_objects(self):
        """Criteria for receipting:
        1. Stripe donation
        2. Registered user
        3. Complete profile (full name, billing address)
        """
        stripe_processor = StripeMultivendorPaymentProcessor.objects.filter(enabled=True)
        (start, end) = to_datetime_range(self.start_date, self.end_date)
        lines = (
            OrderLine.objects.filter(
                created_on__range=(start, end),
                type=OrderLineType.PRODUCT,
                order__payment_method__payment_processor__in=stripe_processor,
                order__customer__isnull=False,
                order__customer__name__isnull=False,
                order__customer__default_billing_address__isnull=False,
                order__payments__purchase_report_data__receipt=True,
            )
            .prefetch_related("order")
            .prefetch_related("order__customer")
            .prefetch_related("order__payments__purchase_report_data")
        )
        if self.charity:
            lines = lines.filter(supplier=self.charity)
        return lines

    def get_data(self):
        data = []
        order_lines = self.get_objects()[: self.get_queryset_row_limit()]
        for line in order_lines:
            donation_amt = line.quantity
            # https://stripe.com/en-ca/pricing
            stripe_fee = (donation_amt * Decimal(".029")) + Decimal(".3")
            data.append(
                {
                    "name": line.order.customer.full_name,
                    "email": line.order.customer.email,
                    "original_donation_amount": float(round(donation_amt, 2)),
                    "donation_amount": float(round(donation_amt - stripe_fee, 2)),
                    "project_name": line.text,
                    "charity_name": line.supplier.name,
                    "addr_name": line.order.customer.default_billing_address.name,
                    "addr_street": line.order.customer.default_billing_address.street,
                    "addr_street2": line.order.customer.default_billing_address.street2,
                    "addr_street3": line.order.customer.default_billing_address.street3,
                    "addr_code": line.order.customer.default_billing_address.postal_code,
                    "addr_city": line.order.customer.default_billing_address.city,
                    "addr_region": line.order.customer.default_billing_address.region,
                    "addr_country": line.order.customer.default_billing_address.country.code,
                }
            )
        return self.get_return_data(data, has_totals=False)

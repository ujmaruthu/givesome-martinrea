# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumIntegerField
from shuup.core.models import OrderLineType, ShuupModel

from givesome.enums import DonationType, GivesomeDonationType


class PurchaseReportData(ShuupModel):
    """For tracking donations made by customers"""

    project = models.ForeignKey("shuup.Product", related_name="purchase_report_data", on_delete=models.PROTECT)
    payment = models.OneToOneField(
        "shuup.Payment", on_delete=models.PROTECT, related_name="purchase_report_data", verbose_name=_("Payment")
    )
    donation_type = EnumIntegerField(DonationType, default=DonationType.ONE_TIME, verbose_name=_("Donation Type"))
    promoting_brand = models.ForeignKey(
        "shuup.Supplier",
        null=True,
        verbose_name=_("Promoting Brand"),
        related_name="purchase_report_data",
        on_delete=models.PROTECT,
    )
    promoting_office = models.ForeignKey(
        "GivesomeOffice",
        null=True,
        verbose_name=_("Promoting Office"),
        related_name="purchase_report_data",
        on_delete=models.PROTECT,
    )
    givecard = models.ForeignKey("Givecard", null=True, related_name="purchase_report_data", on_delete=models.PROTECT)
    receipt = models.BooleanField(verbose_name=_("Donor wants receipt"), default=False)

    class Meta:
        verbose_name = _("Purchase Report Data")
        verbose_name_plural = _("Purchase Report Data")

    @classmethod
    def create_rows(cls, data):
        """Create a list of table rows for the purchase just made."""
        givecard_payments = data.pop("givecard_payments", None)
        if givecard_payments is None:  # Non-Givecard payment
            row = cls.objects.create(**data)
            return [row]
        else:  # Givecard payment
            return cls.objects.bulk_create(
                [cls(payment=payment, givecard=givecard, **data) for (payment, givecard) in givecard_payments]
            )

    def get_brand_name(self):
        return self.promoting_brand.name if self.promoting_brand is not None else ""

    def get_office_name(self):
        return self.promoting_office.name if self.promoting_office is not None else ""


class GivecardPurseCharge(ShuupModel):
    """For tracking transferred funds from Givecard batches to Givesome Purse"""

    purse = models.ForeignKey(
        "givesome.GivesomePurse",
        on_delete=models.PROTECT,
        related_name="purse_charges",
        verbose_name=_("Givesome Purse"),
    )
    batch = models.OneToOneField(
        "givesome.GivecardBatch",
        on_delete=models.PROTECT,
        related_name="givesome_purse_charge",
        verbose_name=_("Givesome Purse Charge"),
    )
    charge_date = models.DateTimeField(editable=False, verbose_name=_("Charge date"))
    charge_amount = models.PositiveIntegerField(
        verbose_name=_("Charge amount"),
        help_text=_("Amount of balance transferred from the Givecard Batch to Givesome Purse"),
    )


class GivesomeDonationData(ShuupModel):
    """For tracking donations made automatically on Givecard expiry or manually from Givesome Purse"""

    donation_type = EnumIntegerField(GivesomeDonationType, verbose_name=_("Donation Type"))
    payment = models.OneToOneField(
        "shuup.Payment", on_delete=models.PROTECT, related_name="givesome_donation_data", verbose_name=_("Payment")
    )
    purse = models.ForeignKey(
        "givesome.GivesomePurse",
        null=True,
        on_delete=models.PROTECT,
        related_name="givesome_donation_data",
        verbose_name=_("Givesome Purse"),
    )
    supplier = models.ForeignKey(
        "shuup.Supplier",
        null=True,
        on_delete=models.PROTECT,
        related_name="givesome_donation_data",
        verbose_name=_("Supplier"),
    )
    office = models.ForeignKey(
        "GivesomeOffice",
        null=True,
        on_delete=models.PROTECT,
        related_name="givesome_donation_data",
        verbose_name=_("Office"),
    )
    batch = models.ForeignKey(
        "givesome.GivecardBatch",
        null=True,
        on_delete=models.PROTECT,
        related_name="givesome_donation_data",
        verbose_name=_("Givecard Batch"),
    )

    def get_project(self):
        return self.payment.order.lines.filter(type=OrderLineType.PRODUCT).first().product

    def get_donor(self):
        if self.purse is not None:
            return self.purse
        if self.office is not None:
            return self.office
        if self.supplier is not None:
            return self.supplier
        return None

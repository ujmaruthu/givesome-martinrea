# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import OrderLineType, OrderStatus, ShopProduct, ShuupModel
from shuup.core.order_creator import OrderCreator, OrderSource
from shuup.utils.money import Money

from givesome.enums import GivesomeDonationType


def create_order_for_donation(project: ShopProduct, amount: int, order_comment="", payment_comment=""):
    if amount > 0:
        source = OrderSource(project.shop)
        source.update(
            status=OrderStatus.objects.get_default_initial(),
            order_date=now(),
            customer_comment=order_comment,
        )
        source.add_line(
            sku=project.product.sku,
            type=OrderLineType.PRODUCT,
            product=project.product,
            supplier=project.suppliers.first(),
            quantity=amount,
            base_unit_price=source.create_price(1),
            text=project.product.safe_translation_getter("name"),
        )
        order = OrderCreator().create_order(source)
        order.create_payment(Money(value=amount, currency=project.shop.currency), description=payment_comment)
        order.status = OrderStatus.objects.get_default_complete()
        order.save()
        return order


class GivesomePurse(ShuupModel):
    shop = models.ForeignKey(
        "shuup.Shop",
        on_delete=models.PROTECT,
        verbose_name=_("shop"),
        related_name="purse",
    )
    supplier = models.OneToOneField(
        "shuup.Supplier",
        on_delete=models.PROTECT,
        verbose_name=_("supplier"),
        related_name="purse",
        null=True,  # Givesome's own purse doesn't have a supplier
    )

    class Meta:
        verbose_name = _("givesome purse")
        verbose_name_plural = _("givesome purses")

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self.supplier is None:
            return "Givesome's Purse"
        return f"{self.supplier}'s Brand Purse"

    @property
    def balance(self):
        sum_charges = self.purse_charges.aggregate(sum=Sum("charge_amount"))["sum"] or 0
        sum_donations = int(
            self.givesome_donation_data.filter(donation_type=GivesomeDonationType.PURSE_MANUAL).aggregate(
                sum=Sum("payment__amount_value")
            )["sum"]
            or 0
        )
        return sum_charges - sum_donations


class GivesomePurseAllocation(ShuupModel):
    purse = models.ForeignKey(
        "givesome.GivesomePurse",
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    shop_product = models.ForeignKey("shuup.ShopProduct", related_name="purse_allocations", on_delete=models.CASCADE)
    weight = models.PositiveIntegerField(default=0, verbose_name=_("weight"))

    class Meta:
        verbose_name = _("givesome purse allocation")
        verbose_name_plural = _("givesome purse allocations")

    def __str__(self):
        return f"{self.purse.name} Allocation ({self.shop_product.get_name()})"

    def get_max_donate_amount(self):
        balance = self.purse.balance
        goal = self.shop_product.product.project_extra.funding_required
        return min(balance, goal)

    def create_manual_donation(self, amount=0):
        from givesome.models import GivesomeDonationData

        if amount == 0:
            raise ValidationError(_("Please enter a non-zero amount."))
        if amount > self.get_max_donate_amount():
            raise ValidationError("You can not donate more than Givesome Purse contains or project can accept.")

        comment = "Givesome Purse Manual Donation"
        order = create_order_for_donation(
            project=self.shop_product, amount=amount, order_comment=comment, payment_comment=comment
        )
        GivesomeDonationData.objects.create(
            purse=self.purse,
            donation_type=GivesomeDonationType.PURSE_MANUAL,
            payment=order.payments.first(),
        )

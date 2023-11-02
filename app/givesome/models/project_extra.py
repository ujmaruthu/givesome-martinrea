# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import math

from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import Order, PaymentStatus, Shop, ShuupModel
from shuup.simple_supplier.models import StockCount

from givesome.admin_module.forms.shop_settings import givesome_fully_funded_display_days


def ensure_project_extra(project):
    project_extra, created = ProjectExtra.objects.get_or_create(project=project, defaults=dict(goal_amount=0))
    if created:
        ensure_project_stock(project)
    return project_extra


def ensure_project_stock(project):
    stock_count, __ = StockCount.objects.get_or_create(
        product=project,
        defaults=dict(
            logical_count=project.project_extra.goal_amount,
            physical_count=project.project_extra.goal_amount,
            supplier=project.project_extra.supplier,
        ),
    )
    return stock_count


class ProductListingQuerySet(models.QuerySet):
    def listed(self, shop=None):
        """
        Returns a qs of products that have not been fully funded
        or were fully funded recently
        """
        shop = shop if shop is not None else Shop.objects.first()
        funded_cutoff_date = timezone.now() - timezone.timedelta(days=givesome_fully_funded_display_days(shop=shop))

        return self.exclude(fully_funded_date__isnull=False, fully_funded_date__lte=funded_cutoff_date)


class ProjectExtra(ShuupModel):
    project = models.OneToOneField(
        "shuup.Product",
        related_name="project_extra",
        on_delete=models.CASCADE,
    )
    goal_amount = models.IntegerField()
    available_from = models.DateTimeField(
        verbose_name=_("Available from date"),
        help_text=_("After this date the project will be visible in the store front."),
        null=True,
        blank=True,
        db_index=True,
    )
    fully_funded_date = models.DateTimeField(
        verbose_name=_("Fully funded date"),
        help_text=_("The date at which the project reached its funding goal."),
        null=True,
        blank=True,
        db_index=True,
    )
    lives_impacted = models.IntegerField(help_text=_("The total number of projected lives to be impacted."), default=0)
    sponsored_by = models.ForeignKey(
        "shuup.Supplier",
        related_name="sponsored_projects",
        verbose_name=_("Sponsored by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    enable_receipting = models.BooleanField(default=False)
    donation_url = models.URLField(
        verbose_name=_("Donation URL"),
        help_text=_("The URL to redirect donors to make a donation to this project."),
        null=True,
        blank=True,
    )

    objects = ProductListingQuerySet.as_manager()

    @property
    def funding_required(self):
        """Amount left until project is fully funded"""
        stock_count = ensure_project_stock(self.project)
        if stock_count is not None:
            amt = (
                int(stock_count.logical_count)
                if not stock_count.logical_count % 1
                else round(stock_count.logical_count, 2)
            )
            # replacing max(amt,0) with amt to return the exact amount donated to the project
            return amt
        return 0

    @property
    def goal_progress_amount(self):
        """Amount of money donated to project, do not show negative amounts"""
        return max(self.goal_amount - self.funding_required, 0)

    @property
    def goal_progress_percentage(self):
        if self.goal_amount == 0:
            return 0
        return math.floor(self.goal_progress_amount / self.goal_amount * 100)
    @property
    def give_now_display(self):
        percent = math.floor(self.goal_progress_amount / self.goal_amount * 100)
        if percent >= 100:
            return False
        return True

    @property
    def last_donation(self):
        string = "Last donation {}"
        last_timestamp = (
            Order.objects.filter(payment_status=PaymentStatus.FULLY_PAID, lines__product=self.project)
            .order_by("-modified_on")
            .first()
        )
        if last_timestamp is None or self.goal_progress_amount == 0:
            return ""

        delta = now() - last_timestamp.modified_on
        if delta.seconds <= 60:
            return _(string.format("a moment ago"))
        elif delta.seconds <= 60 * 60:
            minutes = "{}m ago"
            return _(string.format(minutes.format(delta.seconds // 60)))
        elif delta.days == 0:
            hours = "{}h ago"
            return _(string.format(hours.format(delta.seconds // (60 * 60))))
        else:
            days = "{}d ago"
            return _(string.format(days.format(delta.days)))

    @property
    def supplier(self):
        shop_products = self.project.shop_products.first()
        if shop_products:
            return shop_products.suppliers.first()

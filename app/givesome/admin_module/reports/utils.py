# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.admin.shop_provider import get_shop
from shuup.core.models import Order, OrderLine, Payment
from shuup.utils.dates import to_datetime_range

from givesome.enums import GivesomeDonationType
from givesome.models import Givecard, GivecardCampaign, GivecardPurseCharge, GivesomeDonationData, PurchaseReportData


class BaseMixin:
    start_date = None  # Fix `Unresolved attribute reference` warnings
    end_date = None
    request = None
    options = None

    def get_filter_values(self):
        if not self.shop:
            self.shop = get_shop(self.request)

        self.charity = self.options.get("charity")
        self.brand_vendor = self.options.get("brand_vendor")
        self.offices = self.options.get("offices")
        self.campaign = self.options.get("campaign")
        self.purse = self.options.get("purse")


class GivesomeOrderMixin(BaseMixin):
    def get_order_objects(self):
        """Gets only orders made by users in checkout"""
        self.get_filter_values()
        orders = Order.objects.filter(shop=self.shop).complete().valid().distinct().order_by("-order_date")
        if self.start_date and self.end_date:
            (start, end) = to_datetime_range(self.start_date, self.end_date)
            orders = orders.filter(order_date__range=(start, end))
        return orders

    def get_customer_order_objects(self):
        """Gets only orders made by users in checkout"""
        return self.get_order_objects().filter(payments__purchase_report_data__isnull=False)

    def get_non_customer_order_objects(self):
        """Gets only orders made by automatic or manual donation of expired funds"""
        return self.get_order_objects().filter(
            payments__purchase_report_data__isnull=True, payments__givesome_donation_data__isnull=False
        )

    def get_line_objects(self):
        self.get_filter_values()
        orders = self.get_order_objects()
        order_lines = OrderLine.objects.filter(order__in=orders, supplier__isnull=False)
        if self.charity:
            order_lines = order_lines.filter(supplier=self.charity)
        return order_lines

    def get_charity_order_objects(self):
        orders = self.get_customer_order_objects()
        if self.charity:
            orders = orders.filter(lines__supplier=self.charity).distinct()
        return orders

    def get_brand_order_objects(self):
        orders = self.get_customer_order_objects()
        if self.brand_vendor:
            orders = orders.filter(payments__purchase_report_data__promoting_brand=self.brand_vendor).distinct()
        if self.offices:
            orders = orders.filter(payments__purchase_report_data__promoting_office=self.offices).distinct()
        return orders

    def get_purchase_data_objects(self):
        orders = self.get_charity_order_objects()
        return PurchaseReportData.objects.filter(payment__in=Payment.objects.filter(order__in=orders)).order_by(
            "-payment__order__order_date"
        )

    def filter_by_offices(self, purchases):
        return purchases.filter(promoting_office__in=self.offices) if self.offices else purchases

    def get_givecard_purchase_data_objects(self):
        data = self.get_purchase_data_objects()
        data = self.filter_by_offices(data)
        givecards = self.get_givecard_objects()  # Requires GivecardMixin
        return data.filter(givecard__in=givecards)


class GivecardMixin(BaseMixin):
    def get_campaign_objects(self):
        self.get_filter_values()
        campaigns = GivecardCampaign.objects.all()
        if self.brand_vendor:
            campaigns = campaigns.filter(supplier=self.brand_vendor)
        if self.campaign:
            campaigns = campaigns.filter(pk=self.campaign.pk)
        return campaigns.distinct().order_by("supplier", "identifier")

    def get_givecard_objects(self):
        campaigns = self.get_campaign_objects()
        cards = Givecard.objects.filter(batch__campaign__in=campaigns)
        if self.offices:
            cards = cards.filter(batch__office__in=self.offices)
        return cards

    def get_redeemed_givecard_objects(self):
        # Filters Givecards based on set start and end dates
        givecards = self.get_givecard_objects().filter(redeemed_on__isnull=False).order_by("-redeemed_on")
        if self.start_date and self.end_date:
            (start, end) = to_datetime_range(self.start_date, self.end_date)
            givecards = givecards.filter(redeemed_on__range=(start, end))
        return givecards


class GivesomePurseMixin(BaseMixin):
    def get_purse_charge_objects(self):
        self.get_filter_values()
        charges = GivecardPurseCharge.objects.all()
        if self.purse:
            charges = charges.filter(purse=self.purse)
        if self.campaign:
            charges = charges.filter(batch__campaign=self.campaign)
        if self.start_date and self.end_date:
            (start, end) = to_datetime_range(self.start_date, self.end_date)
            charges = charges.filter(charge_date__range=(start, end))
        return charges.order_by("-charge_date")

    def get_manual_donation_data_objects(self):
        orders = self.get_non_customer_order_objects()  # Requires GivesomeOrderMixin
        return GivesomeDonationData.objects.filter(
            payment__in=Payment.objects.filter(order__in=orders),
            batch__isnull=True,
            donation_type=GivesomeDonationType.PURSE_MANUAL,
        )

    def get_automatic_donation_data_objects(self):
        orders = self.get_non_customer_order_objects()  # Requires GivesomeOrderMixin
        data = GivesomeDonationData.objects.filter(
            payment__in=Payment.objects.filter(order__in=orders),
        ).exclude(donation_type=GivesomeDonationType.PURSE_MANUAL)

        if self.campaign:
            data.filter(batch__campaign=self.campaign)  # Requires GivecardMixin
        return data

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import json
from argparse import ArgumentTypeError
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import activate
from shuup.core.models import (
    Category,
    Order,
    OrderLine,
    Payment,
    PersonContact,
    Product,
    ShopProduct,
    Supplier,
    SupplierShop,
)
from shuup.simple_supplier.models import StockCount
from shuup_multivendor.models import SupplierPrice
from shuup_stripe_multivendor.models import StripeCustomer

from givesome.enums import GivecardBatchExpiryType, GivecardDonateRestrictionType
from givesome.models import (
    CompletionVideo,
    Givecard,
    GivecardBatch,
    GivecardCampaign,
    OffPlatformDonation,
    ProjectExtra,
    VendorExtra,
    VolunteerHours,
)

models = [
    GivecardCampaign,
    Givecard,
    GivecardBatch,
    Payment,
    OrderLine,
    Order,
    CompletionVideo,
    ShopProduct,
    Category,
    ProjectExtra,
    Product,
    StockCount,
    SupplierPrice,
    SupplierShop,
    VendorExtra,
    Supplier,
    OffPlatformDonation,
    VolunteerHours,
    StripeCustomer,
    PersonContact,
    User,
]


def json_file(filename):
    """Validate that `filename` has a json extension."""
    if not filename.endswith(".json"):
        raise ArgumentTypeError("Please provide the path to a json file for data input.")
    return filename


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--path", type=json_file, required=True, help="Path to target data file.")

    def create_campaign(self, campaign_data):
        campaign, __ = GivecardCampaign.objects.get_or_create(
            identifier=campaign_data["identifier"],
            defaults=dict(
                name=campaign_data["name"],
                message=campaign_data["message"],
                supplier=campaign_data["supplier"],
            ),
        )
        return campaign

    def create_batch(self, batch_data):
        batch, created = GivecardBatch.objects.get_or_create(
            campaign=batch_data["campaign"],  # Only one batch per campaign
            defaults=dict(
                created_on=timezone.now(),
                generated_on=timezone.now(),
                supplier=batch_data["supplier"],
                value=20,
                amount=len(batch_data["givecards"]),
                code=None,
                restriction_type=GivecardDonateRestrictionType.DISABLED,
                expiry_type=GivecardBatchExpiryType.MANUAL,
                redemption_end_date=date(year=2021, month=5, day=31),
                expiration_date=date(year=2021, month=6, day=30),
            ),
        )
        if created:
            givecards = [Givecard(batch=batch, code=code, balance=20) for code in batch_data["givecards"]]
            Givecard.objects.bulk_create(givecards)

    @atomic
    def _migrate(self, json_data):
        for data in json_data:
            supplier = Supplier.objects.filter(name="Martinrea USA - BCA").first()
            campaign_data = {
                "identifier": data["campaign_id"],
                "name": "Martinrea",
                "message": "At Martinrea, we are committed to being positive contributors to our communities. With "
                "this $20 donation you can help support our vision and mission. Thank you for choosing to "
                "get involved, to help create positive change and to pay our success forward.",
                "supplier": supplier,
            }
            campaign = self.create_campaign(campaign_data)

            batch_data = {
                "campaign": campaign,
                "supplier": supplier,
                "givecards": data["givecards"],
            }
            self.create_batch(batch_data)

    def handle(self, *args, **options):
        """
        A required "--path" option should contain the path to the exported data.

        E.g. migrate_martinrea_givecards --path /path/to/data.json
        """
        from django.utils.timezone import localtime

        now = localtime()
        activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)

        json_data = None
        try:
            with open(options["path"]) as file:
                json_data = file.read()
                json_data = json.loads(json_data)
        except FileNotFoundError:
            print("File not found. Please check your path and filename.")

        self._migrate(json_data)

        print(f"Runtime: {localtime() - now}")

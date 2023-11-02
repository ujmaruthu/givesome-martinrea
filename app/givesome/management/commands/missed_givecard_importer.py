# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import json
import re
from datetime import datetime

import firebase_admin
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import Q
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import activate
from firebase_admin import auth
from firebase_admin._auth_utils import UserNotFoundError
from shuup.core.models import PersonContact, Shop

from givesome.management.commands.migrate_givesome_data import _get_givecard_balance, json_file
from givesome.models import Givecard, GivecardBatch, GivecardCampaign


def _get_timestamp(timestamp: int):
    if timestamp is not None:
        return datetime.fromtimestamp(int(str(timestamp)[:10]))


class Command(BaseCommand):
    """
    A required "--path" option should contain the path to the exported data.

    E.g. migrate_givesome_data --path /path/to/data.json --dry 1 --verbose 1
    """

    givesome_data = None
    options = None
    shop = Shop.objects.first()
    ignored_campaigns = ["test-entity", "brentwood"]

    def add_arguments(self, parser):
        parser.add_argument("--path", type=json_file, required=True, help="Path to target data file.")
        parser.add_argument("--dry", required=False, help="Do not create any Campaigns or Givecards.")
        parser.add_argument("--verbose", required=False, help="Print Campaigns and Givecards being created.")

    def _get_unmigrated_givecards(self):  # noqa: C901
        cutoff_cate = datetime(2021, 5, 30)
        valid_givecards = set()

        multi_redeemed_codes = set()
        # Some givecards have been redeemed more than once
        # We need to keep track of spent givecards and not include them in valid givecards
        spent_givecards = set()

        old_givecard_data = self.givesome_data["givecards"]["cards"]

        # Get unexpired Givecards that have been redeemed and have funds left
        old_users = self.givesome_data["users"]
        for user_key, user in old_users.items():
            if (
                type(user) == dict  # Original data is pretty bad
                and "accounts" in user
                and "givecards" in user["accounts"]
            ):
                user_givecards = user["accounts"]["givecards"]
                for givecard_code in user_givecards:
                    user_givecard = user_givecards[givecard_code]
                    if "value" not in user_givecard:  # Some givecards are missing value
                        continue
                    if int(user_givecard["value"]) <= 0:  # Some givecards have value as string
                        spent_givecards.add(givecard_code)
                        continue
                    if _get_timestamp(old_givecard_data[givecard_code]["expires"]) < cutoff_cate:
                        continue
                    if len(givecard_code) < 6:
                        continue
                    if "entity" in user_givecard and user_givecard["entity"] in self.ignored_campaigns:
                        continue
                    if "entity" not in user_givecard:
                        continue
                    # Givecard has funds and is not expired
                    if givecard_code in valid_givecards:
                        multi_redeemed_codes.add(givecard_code)
                    valid_givecards.add(givecard_code)

        # Remove any Spent givecards
        valid_givecards = set([code for code in valid_givecards if code not in spent_givecards])

        # Get unredeemed givecards
        for code, givecard in old_givecard_data.items():
            if _get_timestamp(givecard["expires"]) < cutoff_cate:
                continue
            if "redeemed-date" in givecard:
                continue
            if "multi-use" in givecard:  # All non-migrated multicards are test cards
                continue
            if len(code) < 6:
                continue
            if "entity" in givecard and givecard["entity"] in self.ignored_campaigns:
                continue
            if "entity" not in givecard:
                continue
            # Unredeemed and not redeemed
            valid_givecards.add(code)

        # Go through Givecard Donations to find any cards that have been fully spent already
        donated_amounts = {}
        for key, donation in self.givesome_data["givecard-donations"].items():
            if "card" in donation and donation["card"] in valid_givecards:
                code = donation["card"]
                if code in donated_amounts:
                    donated_amounts[code] = donated_amounts[code] + donation["amount"]
                else:
                    donated_amounts[code] = donation["amount"]
        for code, donated in donated_amounts.items():
            gc = old_givecard_data[code]
            if "value" in gc and gc["value"] <= donated:
                valid_givecards.remove(code)

        # Get migrated Givecards
        migrated_givecards = Givecard.objects.filter(code__in=valid_givecards).values_list("code", flat=True).distinct()
        migrated_multicards = (
            GivecardBatch.objects.filter(code__in=valid_givecards).values_list("code", flat=True).distinct()
        )
        migrated_givecard_codes = set(list(migrated_givecards) + list(migrated_multicards))

        unmigrated_givecards = valid_givecards.difference(migrated_givecard_codes)

        return unmigrated_givecards

    def _group_givecards_by_campaign(self, unmigrated_givecard_codes):
        old_givecards = self.givesome_data["givecards"]["cards"]

        campaigns = {}
        for code in unmigrated_givecard_codes:
            givecard = old_givecards[code]
            campaign = givecard["entity"]

            if campaign in self.ignored_campaigns:
                continue

            if campaign not in campaigns:
                campaigns[campaign] = {}
            campaigns[campaign][code] = givecard

        if self.options["verbose"]:
            for campaign, givecards in campaigns.items():
                print(campaign)
                for code, givecard in givecards.items():
                    print(
                        f"- {code}, "
                        f"Exp: {_get_timestamp(givecard['expires']).date()}, "
                        f"Redeemed: {'redeemed-date' in givecard and _get_timestamp(givecard['redeemed-date']) or 'No'}"
                        f", Value {'value' in givecard and givecard['value']}"
                    )
            print(f"Total Campaigns: {len(campaigns)}")
            print(f"Total Givecards: {len(unmigrated_givecard_codes)}")
        return campaigns

    @atomic
    def _migrate(self):  # noqa C901
        unmigrated_givecards = self._get_unmigrated_givecards()  # Set of Givecard codes
        campaigns = self._group_givecards_by_campaign(unmigrated_givecards)
        old_campaigns = self.givesome_data["givecards"]["entities"]

        firebase_admin.initialize_app()

        for campaign_name, givecards in campaigns.items():
            campaign, created = GivecardCampaign.objects.get_or_create(identifier=campaign_name)
            if created:
                campaign.name = " ".join(re.split("[-_]", campaign_name))
                campaign.message = old_campaigns[campaign_name]["message"]
                campaign.save()

            # Campaigns in db dump only have multicard or unique givecard batches, never both
            is_multicard = "multi-use" in next(iter(givecards.values()))  # Just get the value from first givecard
            expiry_date = max(set(gc["expires"] for gc in list(givecards.values())))  # Get latest expiry date
            expiry_date = _get_timestamp(expiry_date).date()
            if expiry_date == datetime(2021, 5, 31).date():
                expiry_date = datetime(2021, 7, 31).date()
            values = set([gc["value"] for gc in list(givecards.values())])

            if not is_multicard:
                # Create batches for every value
                for value in values:
                    if value <= 1:
                        continue

                    # Givecards that will be added to batch
                    batch_givecards = {}
                    for code, givecard in givecards.items():
                        if givecard["value"] == value:
                            batch_givecards[code] = givecard

                    batch = GivecardBatch.objects.create(
                        campaign=campaign,
                        generated_on=timezone.now(),
                        redemption_end_date=expiry_date,
                        amount=len(batch_givecards),
                        value=value,
                    )
                    for code, givecard in batch_givecards.items():
                        gc = Givecard(
                            batch=batch,
                            code=code,
                            balance=givecard["value"],
                        )
                        if "redeemed-date" in givecard:
                            gc.redeemed_date = givecard["redeemed-date"]
                            if "redeemed-by" in givecard:
                                new_balance = _get_givecard_balance(self.givesome_data, givecard["redeemed-by"], code)
                                if new_balance:
                                    gc.balance = new_balance
                                try:
                                    # Create a user for the Givecard
                                    firebase_user = auth.get_user(givecard["redeemed-by"])
                                    if firebase_user.email:
                                        user = User.objects.filter(
                                            Q(username=firebase_user.email) | Q(username=firebase_user.email)
                                        ).first()
                                        if user is not None:
                                            gc.user = user
                                        else:
                                            django_user = User(username=firebase_user.email, email=firebase_user.email)
                                            django_user.save()
                                            person_contact = PersonContact(
                                                name=firebase_user.display_name or "",
                                                email=firebase_user.email,
                                                shop=self.shop,
                                                user=django_user,
                                            )
                                            person_contact.save()
                                except UserNotFoundError as e:
                                    print(e)
                        gc.save()

                # Some Givecards had a portion of its balance spent.
                # Check Givecard balance from users and update it to created Givecards
                for code, givecard in givecards.items():
                    if "redeemed-by" in givecard:
                        user_id = givecard["redeemed-by"]
                        user_givecards = self.givesome_data["users"][user_id]["accounts"]["givecards"]
                        if code in user_givecards:
                            value = user_givecards[code]["value"]
                            if value != givecard["value"]:  # Update price only if its different than the original
                                Givecard.objects.filter(code=code).update(balance=value)
            else:
                # All non-migrated multicards are test cards
                pass

        if self.options["dry"]:
            raise Exception("This was a dry run. Creation of objects prevented with this exception")

        print(f"Created {len(campaigns)} campaigns")
        print(f"Created {len(unmigrated_givecards)} Givecards")

    def handle(self, *args, **options):
        activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)

        try:
            with open(options["path"]) as file:
                self.givesome_data = file.read()
                self.givesome_data = json.loads(self.givesome_data)
        except FileNotFoundError:
            print("File not found. Please check your path and filename.")

        self.options = options
        self._migrate()

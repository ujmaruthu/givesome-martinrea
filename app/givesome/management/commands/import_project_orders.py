# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import json
from datetime import datetime
from functools import lru_cache

import firebase_admin
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.transaction import atomic
from django.utils.crypto import get_random_string
from django.utils.timezone import make_aware
from django.utils.translation import activate
from firebase_admin import auth
from shuup.core.models import (
    Order,
    OrderLine,
    OrderLineType,
    OrderStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Product,
    Shop,
)
from shuup.core.pricing import TaxfulPrice
from shuup_stripe_multivendor.models import StripeMultivendorPaymentProcessor

from givesome.management.commands.migrate_givesome_data import json_file


class Command(BaseCommand):
    """
    A required "--path" option should contain the path to the exported data.

    Example run:
    python -W ignore manage.py import_project_orders --path givesome-export.json --dry 1
    """

    givesome_data = None
    options = None
    shop = Shop.objects.first()
    complete_status = OrderStatus.objects.filter(identifier="complete").first()
    timestamp = make_aware(datetime(2020, 1, 1))  # Donations don't have any date info
    stripe_payment_method = PaymentMethod.objects.filter(
        payment_processor=StripeMultivendorPaymentProcessor.objects.filter(enabled=True).first()
    ).first()

    def add_arguments(self, parser):
        parser.add_argument("--path", type=json_file, required=True, help="Path to target data file.")
        parser.add_argument("--dry", required=False, help="Do not create any orders.")

    def get_donations_from_projects(self) -> dict:
        """returns: {"uid": set("project_id", ...)", ...}"""
        all_project_data = self.givesome_data["projects"]

        data = {}
        for key, project in all_project_data.items():
            if "donators" not in project or "donation-amounts" not in project:
                continue
            for uid in project["donators"].keys():
                if uid not in data:
                    data[uid] = set()
                data[uid].add(key)
            for uid in project["donation-amounts"].keys():
                if uid not in data:
                    data[uid] = set()
                data[uid].add(key)
        return data

    def pop_cash_and_givecard_projects(self, data) -> dict:
        """
        Remove any projects that users have donated with Cash or Givecards
        """
        cash_donations = self.givesome_data["cash-donations"]
        givecard_donations = self.givesome_data["givecard-donations"]

        def _pop_project(donation):
            if "user" in donation and "project" in donation:
                uid = donation["user"]
                if uid in data:
                    data[uid].discard(donation["project"])

        for __, donation in cash_donations.items():
            _pop_project(donation)
        for ref, donation in givecard_donations.items():
            _pop_project(donation)
        return data

    def get_missing_data(self) -> dict:
        projects = self.get_donations_from_projects()
        projects = self.pop_cash_and_givecard_projects(projects)
        return projects

    @lru_cache()
    def get_product(self, project_id):
        headline = self.givesome_data["projects"][project_id]["headline"]
        product = Product.objects.filter(translations__name=headline).first()
        if product is not None:
            return product

        # Some project original headlines have whitespace at the end,
        # but the projects have been edited in Shuup prod, which strips the whitespace away away
        headline = headline.strip()
        product = Product.objects.filter(translations__name=headline).first()
        if product is not None:
            return product

    def create_user_orders(self, contact, uid, user_projects: set):
        for project_id in user_projects:
            donations = self.givesome_data["projects"][project_id]["donation-amounts"]
            # There are some donations, that dont have a donation amount, default to 1
            # These donations are still imported to increase users' lives impacted value
            donation_amount = donations[uid] if uid in donations else 1
            product = self.get_product(project_id)

            order = Order.objects.create(
                shop=self.shop,
                key=get_random_string(32),
                customer=contact,
                payment_date=self.timestamp,
                payment_method=self.stripe_payment_method,
                payment_status=PaymentStatus.FULLY_PAID,
                status=self.complete_status,
                taxful_total_price_value=donation_amount,
                taxless_total_price_value=donation_amount,
                prices_include_tax=True,
                order_date=self.timestamp,
            )
            OrderLine.objects.create(
                base_unit_price=TaxfulPrice(1, settings.SHUUP_HOME_CURRENCY),
                quantity=donation_amount,
                product=product,
                supplier=product.get_shop_instance(self.shop).suppliers.first(),
                created_on=self.timestamp,
                order=order,
            )
            OrderLine.objects.create(quantity=1, type=OrderLineType.PAYMENT, created_on=self.timestamp, order=order)
            payment = Payment.objects.create(
                payment_identifier=f"{order.id}:1",
                amount_value=order.taxless_total_price_value,
                description=f"Migrated Donation # {order.id} from projects table",
                order=order,
            )
            payment.created_on = payment.order.created_on
            payment.save()

    def _migrate(self):
        missing_data = self.get_missing_data()
        num_users = 0  # Number or users affected
        num_orders = 0

        print("Starting order migration for", len(missing_data), "users!")
        # Iterating through all firebase users and validating them locally is
        # much faster than fetching only users from firebase that we need
        for firebase_user in auth.list_users().iterate_all():
            # Ignore anonymous users, Skip if user is not in prefiltered list
            if not firebase_user.email or not firebase_user.uid or firebase_user.uid not in missing_data.keys():
                continue

            user_projects = missing_data[firebase_user.uid]
            # Skip users whose orders dont need to be imported
            if not len(user_projects):
                continue

            # Ignore users that are not on the platform already
            user = User.objects.filter(username=firebase_user.email).first()
            if user is None:
                continue

            self.create_user_orders(user.contact, firebase_user.uid, user_projects)

            # Statistics!
            if num_users % 20 == 0:
                print(num_users, "users,", num_orders, "orders processed...")
            num_users += 1
            num_orders += len(user_projects)
        print("Done!", num_users, "users and", num_orders, "orders processed!")

    @atomic()
    def handle(self, *args, **options):
        from django.utils.timezone import localtime

        now = localtime()
        activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)
        try:
            with open(options["path"]) as file:
                self.givesome_data = file.read()
                self.givesome_data = json.loads(self.givesome_data)
        except FileNotFoundError:
            print("File not found. Please check your path and filename.")

        self.options = options
        firebase_admin.initialize_app()
        self._migrate()

        print(localtime() - now)

        if self.options["dry"]:
            raise Exception("This was a dry run. Creation of objects prevented with this exception")

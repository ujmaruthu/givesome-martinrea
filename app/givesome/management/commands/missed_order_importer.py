# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import json
from functools import lru_cache
from typing import Optional

import firebase_admin
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import IntegerField, Q
from django.db.models.functions import Cast
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import make_aware
from django.utils.translation import activate
from firebase_admin import auth
from firebase_admin._auth_utils import UserNotFoundError
from shuup.core.models import (
    Order,
    OrderLine,
    OrderLineType,
    OrderStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    PersonContact,
    Product,
    ProductVisibility,
    SalesUnit,
    ShippingMode,
    Shop,
    ShopProduct,
    Supplier,
    TaxClass,
)
from shuup.core.pricing import TaxfulPrice
from shuup.simple_supplier.models import StockCount
from shuup_multivendor.models import SupplierPrice
from shuup_stripe_multivendor.models import StripeMultivendorPaymentProcessor

from givesome.enums import VendorExtraType
from givesome.management.commands.migrate_givesome_data import json_file
from givesome.management.commands.missed_givecard_importer import _get_timestamp
from givesome.models import GivecardPaymentProcessor, ProjectExtra, VendorExtra


@lru_cache()
def get_or_create_firebase_user(fb_uid: str) -> Optional[User]:
    try:
        firebase_user = auth.get_user(fb_uid)
        if firebase_user.email:
            # Find user if its already been created
            user = User.objects.filter(Q(username=firebase_user.email) | Q(username=firebase_user.email)).first()
            if user is not None:
                return user

            # No user found, create one
            user = User(username=firebase_user.email, email=firebase_user.email)
            user.save()
            person_contact = PersonContact(
                name=firebase_user.display_name or "",
                email=firebase_user.email,
                user=user,
            )
            person_contact.save()
            return user
    except UserNotFoundError as e:
        print(e)


class Command(BaseCommand):
    """
    A required "--path" option should contain the path to the exported data.

    E.g. python -W ignore manage.py migrate_givesome_data --path data.json --orders orders.json --dry 1 --verbose 1
    """

    givesome_data = None
    options = None
    shop = Shop.objects.first()
    tax_class = TaxClass.objects.filter(identifier="product").first()
    sales_unit = SalesUnit.objects.filter(identifier="pcs").first()
    created_orders = 0
    created_products = 0
    created_suppliers = 0
    last_sku = 0

    def add_arguments(self, parser):
        parser.add_argument("--path", type=json_file, required=True, help="Path to target data file.")
        parser.add_argument(
            "--orders",
            type=json_file,
            required=True,
            help="Path to target data containing the orders",
        )
        parser.add_argument("--dry", required=False, help="Do not create any orders.")
        parser.add_argument("--verbose", required=False, help="Print orders being created.")

    def _get_order_objects(self) -> (dict, dict):
        cash_orders = {}
        givecard_orders = {}

        cash_donations = self.givesome_data["cash-donations"]
        givecard_donations = self.givesome_data["givecard-donations"]
        all_projects = self.givesome_data["projects"]
        missing_amount = 0
        missing_projects = 0

        print(len(self.orders), "missing orders recorded")

        for o in self.orders:
            if o in cash_donations:
                if "amount" in cash_donations[o]:
                    if "project" in cash_donations[o] and cash_donations[o]["project"] in all_projects:
                        cash_orders[o] = cash_donations[o]
                    else:
                        missing_projects += 1
                else:
                    missing_amount += 1

            elif o in givecard_donations:
                if "amount" in givecard_donations[o]:
                    if "project" in givecard_donations[o] and givecard_donations[o]["project"] in all_projects:
                        givecard_orders[o] = givecard_donations[o]
                    else:
                        missing_projects += 1
                else:
                    missing_amount += 1

        sum_orders = len(cash_orders) + len(givecard_orders)
        print(sum_orders, "orders found")
        print("ERR:", missing_amount, "orders with missing amounts")
        print("ERR:", missing_projects, "orders with missing projects")
        if len(self.orders) - sum_orders > missing_amount + missing_projects:
            print(len(self.orders) - sum_orders - missing_amount - missing_projects, "invalid orders found")

        return (cash_orders, givecard_orders)

    def _get_or_create_charity(self, organization: dict):
        charity, created = Supplier.objects.get_or_create(
            name=organization["name"],
            givesome_extra__vendor_type=VendorExtraType.CHARITY,
            deleted=False,
            defaults=dict(
                stock_managed=True,
                module_identifier=settings.SHUUP_MULTIVENDOR_SUPPLIER_MODULE_IDENTIFIER,
            ),
        )
        if created:
            print("Created charity:", organization["name"])
            self.created_suppliers += 1
            url = organization.get("link")[:128] if organization.get("link") else None
            VendorExtra.objects.create(
                vendor=charity,
                website_url=url,
                allow_brand_page=False,
                vendor_type=VendorExtraType.CHARITY,
            )
        return charity

    def _create_project(self, firebase_project: dict) -> Product:
        self.created_products += 1
        charity = self._get_or_create_charity(firebase_project["organization"])

        identifier = "-".join(firebase_project["headline"].split(" "))
        print("Created project:", firebase_project["headline"])

        if self.last_sku == 0:
            self.last_sku = (
                Product.objects.filter(sku__regex=r"^[0-9]+$")
                .annotate(sku_int=Cast("sku", IntegerField()))
                .order_by("-sku_int")
                .first()
                .sku_int
            )
        self.last_sku += 1
        givesome_project = Product.objects.create(
            shipping_mode=ShippingMode.NOT_SHIPPED,
            tax_class=self.tax_class,
            sales_unit=self.sales_unit,
            description=firebase_project.get("description") or "",
            name=firebase_project["headline"],
            slug=identifier,
            sku=self.last_sku,
        )

        raised = firebase_project.get("raised") or 0
        if firebase_project.get("fulfilled") and raised < firebase_project["goal"]:
            # Project was closed out raise `raised` up to goal if needed
            raised = firebase_project["goal"] if firebase_project["goal"] > raised else raised
        StockCount.objects.create(
            product=givesome_project, supplier=charity, logical_count=firebase_project["goal"] - raised
        )

        ProjectExtra.objects.create(
            project=givesome_project,
            goal_amount=firebase_project["goal"],
            lives_impacted=firebase_project.get("people-impacted-count") or 0,
            fully_funded_date=timezone.now() if firebase_project["goal"] <= raised else None,
        )

        shop_product = ShopProduct.objects.create(
            name=firebase_project["headline"],
            description=firebase_project.get("description"),
            default_price=TaxfulPrice(1, settings.SHUUP_HOME_CURRENCY),
            product=givesome_project,
            shop=self.shop,
            visibility_limit=ProductVisibility.VISIBLE_TO_ALL,
        )
        shop_product.suppliers.add(charity)

        SupplierPrice.objects.create(
            shop=self.shop,
            product=givesome_project,
            supplier=charity,
            amount=TaxfulPrice(1, settings.SHUUP_HOME_CURRENCY),
        )

        return givesome_project

    @lru_cache()
    def _get_or_create_project(self, project_id: str):
        firebase_project = self.givesome_data["projects"][project_id]
        product = Product.objects.filter(translations__name=firebase_project["headline"]).first()
        if not product:
            product = self._create_project(firebase_project)
        return product

    def _create_orders(self, firebase_orders, payment_method):
        complete = OrderStatus.objects.filter(identifier="complete").first()
        for ref, donation in firebase_orders.items():
            if not donation["project"]:
                continue
            project = self._get_or_create_project(donation["project"])

            # Get order customer
            contact = None
            if "user" in donation:
                user = get_or_create_firebase_user(donation["user"])
                if user is not None:
                    contact = user.contact

            # Create order
            timestamp = make_aware(_get_timestamp(donation["timestamp"]))
            order = Order.objects.create(
                shop=self.shop,
                key=get_random_string(32),
                customer=contact,
                payment_date=timestamp,
                payment_method=payment_method,
                payment_status=PaymentStatus.FULLY_PAID,
                status=complete,
                taxful_total_price_value=donation["amount"],
                taxless_total_price_value=donation["amount"],
                prices_include_tax=True,
                order_date=timestamp,
            )

            # Order lines
            OrderLine.objects.create(
                base_unit_price=TaxfulPrice(1, settings.SHUUP_HOME_CURRENCY),
                quantity=donation["amount"],
                product=project,
                supplier=project.get_shop_instance(self.shop).suppliers.first(),
                created_on=timestamp,
                order=order,
            )
            OrderLine.objects.create(quantity=1, type=OrderLineType.PAYMENT, created_on=timestamp, order=order)

            # Payment
            payment = Payment.objects.create(
                payment_identifier=f"{order.id}:1",
                amount_value=order.taxless_total_price_value,
                description=f"Migrated Payment for Donation # {order.id}",
                order=order,
            )
            payment.created_on = payment.order.created_on
            payment.save()
            self.created_orders += 1

    def _migrate(self):
        cash_orders, givecard_orders = self._get_order_objects()  # dicts

        # Stripe payments
        payment_method = PaymentMethod.objects.filter(
            payment_processor=StripeMultivendorPaymentProcessor.objects.filter(enabled=True).first()
        ).first()
        self._create_orders(cash_orders, payment_method)

        # Givecard payments
        payment_method = PaymentMethod.objects.filter(
            payment_processor=GivecardPaymentProcessor.objects.filter(enabled=True).first()
        ).first()
        self._create_orders(givecard_orders, payment_method)

        print(self.created_orders, "Orders created")
        print(self.created_suppliers, "Charities created")
        print(self.created_products, "Projects created")

    @atomic()
    def handle(self, *args, **options):
        activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)

        try:
            with open(options["path"]) as file:
                self.givesome_data = file.read()
                self.givesome_data = json.loads(self.givesome_data)
            with open(options["orders"]) as file:
                self.orders = file.read()
                self.orders = json.loads(self.orders)
                self.orders = set(self.orders["orders"])
        except FileNotFoundError:
            print("File not found. Please check your path and filename.")

        self.options = options
        firebase_admin.initialize_app()
        self._migrate()

        if self.options["dry"]:
            raise Exception("This was a dry run. Creation of objects prevented with this exception")

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import calendar
import json
import re
from argparse import ArgumentTypeError
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

import firebase_admin
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.db.transaction import atomic
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from firebase_admin import auth
from shuup.core.models import (
    Category,
    Gender,
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
    SupplierShop,
    TaxClass,
)
from shuup.core.pricing import TaxfulPrice, TaxlessPrice
from shuup.simple_supplier.models import StockCount
from shuup_multivendor.models import SupplierPrice
from shuup_stripe_multivendor.models import StripeCustomer, StripeMultivendorPaymentProcessor

from givesome.enums import GivecardBatchExpiryType, GivecardDonateRestrictionType, VendorExtraType
from givesome.models import (
    CompletionVideo,
    Givecard,
    GivecardBatch,
    GivecardCampaign,
    GivecardPaymentProcessor,
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


def cleanup(pre_existing: Dict[str, List[int]]):
    """Don't leave half-migrated client-owned data in my database."""
    global models

    for model in models:
        dont_delete = pre_existing[model.__name__]
        try:
            count, _ = model.objects.exclude(id__in=dont_delete).delete()
            print(f"deleted {count} {model.__name__} object(s).")
        except Exception as e:
            print(f"failed to delete {model.__name__}", e.args[0])


def json_file(filename):
    """Validate that `filename` has a json extension."""
    if not filename.endswith(".json"):
        raise ArgumentTypeError("Please provide the path to a json file for data input.")
    return filename


def _get_givecard_balance(givesome_data, redeemer: str, code: str) -> int:
    """Sift through unreliable data to hopefully come up with the card balance"""
    try:
        balance = givesome_data["users"][redeemer]["accounts"]["givecards"][code]["value"]
    except KeyError as ke:
        if ke.args[0] is None:
            print(f"Redeemer missing from card {code}")
        elif ke.args[0] == "givecards":
            print(f"unable to find any givecards in user account {redeemer}. User was probably anonymous.")
        else:
            print(f"Unable to find the card in the user's account: {redeemer}, {ke.args[0]}")
        balance = 0

    try:
        return int(balance)
    except ValueError:
        print(f"unable to determine givecard balance: {code}, {balance}")
        return 0


class Command(BaseCommand):
    givesome_data = None
    main_shop = None
    origin = None
    # firebase key, username
    users: Dict[str, str] = {}
    # firebase key, product sku
    projects: Dict[str, str] = {}
    # project id, Supplier instance
    charities: Dict[int, Supplier] = {}
    donations: Dict[str, List[str]] = {}  # i.e. givecard code, list of order refs
    final_expiration: date = date(year=2021, month=6, day=30)
    limit = 100

    def add_arguments(self, parser):
        parser.add_argument("--path", type=json_file, required=True, help="Path to target data file.")
        parser.add_argument(
            "--origin",
            type=str,
            required=False,
            default="https://givesome.shuup.com",
            help="Scheme and domain of target application. Default: https://givesome.shuup.com",
        )

    @staticmethod
    def _format_dob(dob: str, email: str) -> Optional[date]:
        """Attempt to reformat DOBs to a date object. The most common format is 'Sept 10, 1990', and the second
        most common is '1990-09-10. Nothing is guaranteed to be valid, and other formats are present."""
        if type(dob) is str:

            date_parts = re.split(" | ,|-", dob)
            if len(date_parts) != 3:
                # unsupported or incorrect format
                return None

            numeric_format = date_parts[0].isnumeric()

            year = date_parts[0] if numeric_format else date_parts[2]
            day = date_parts[2] if numeric_format else date_parts[1]
            if not numeric_format:
                try:
                    month = list(calendar.month_abbr).index(date_parts[0][:3])
                except ValueError:
                    print(f"Unsupported abbreviation. User: {email}, dob: {dob}")
                    return None
            else:
                month = date_parts[1]

            try:
                birthday = date(year=int(year), month=int(month), day=int(day))
            except ValueError:
                # incorrect format
                birthday = None

            return birthday

    @staticmethod
    def _get_gender(gender: str):
        """Attempt to format `gender`. Data is not guaranteed to be valid or recognizable."""
        if type(gender) is str:
            ch = gender[0].lower()
            if ch in ["u", "m", "f", "o"]:
                return Gender(ch)
        return Gender("u")

    @staticmethod
    def _get_timestamp(timestamp: int):
        if timestamp is not None:
            return datetime.fromtimestamp(int(str(timestamp)[:10]), tz=timezone.utc)

    def _migrate_users(self):  # noqa: C901
        existing_emails = set(User.objects.all().values_list("email", flat=True))
        person_contacts = []
        imported_users: Dict[str, User] = {}
        stripe_customers = []
        volunteer_hours = []
        offplatform_donations = []
        stripe = StripeMultivendorPaymentProcessor.objects.filter(enabled=True).first()

        firebase_admin.initialize_app()

        for firebase_user in auth.list_users().iterate_all():
            givesome_user = self.givesome_data["users"].get(firebase_user.uid)

            if firebase_user.email and firebase_user.email not in existing_emails and givesome_user is not None:
                django_user = User(username=firebase_user.email, email=firebase_user.email)
                person_contact = PersonContact(
                    name=firebase_user.display_name or "",
                    email=firebase_user.email,
                    shop=self.main_shop,
                    user=django_user,
                    gender=self._get_gender(givesome_user.get("gender")),
                    birth_date=self._format_dob(givesome_user.get("dob"), firebase_user.email),
                )

                person_contact.name = firebase_user.display_name or ""
                person_contacts.append(person_contact)

                if givesome_user.get("stripe-id"):
                    stripe_customers.append(
                        StripeCustomer(
                            payment_processor=stripe, contact=person_contact, stripe_id=givesome_user["stripe-id"]
                        )
                    )

                if givesome_user.get("volunteer-hours"):
                    for __, details in givesome_user["volunteer-hours"].items():
                        volunteer_hours.append(
                            VolunteerHours(
                                donor=person_contact,
                                hours=details.get("hours") or 0,
                                volunteered_on=self._get_timestamp(details["date"]),
                                description=details["location"],
                            )
                        )
                if givesome_user.get("other-donations"):
                    for __, details in givesome_user["other-donations"].items():
                        amt = details.get("amount")
                        if type(details.get("amount")) is str:
                            amt = int(amt)
                        if amt > 999:
                            # OffPlatformDonation allows a max of 999 and up to two digits, and some of these
                            # quantities seem to be intended as floats, not ints (e.g. 2500 probably means 25.00).
                            # Don't crash the migration, at any rate.
                            amt = Decimal(str(amt / 100))
                        offplatform_donations.append(
                            OffPlatformDonation(
                                donor=person_contact,
                                amount=amt,
                                donated_on=self._get_timestamp(details["date"]),
                                description=details["location"],
                            )
                        )
                imported_users[firebase_user.uid] = django_user

        users = [user for user in imported_users.values()]
        try:
            User.objects.bulk_create(users)
        except Exception as e:
            print("failed to create Users", e.args[0])
        self.users = {firebase_key: user.username for firebase_key, user in imported_users.items()}
        try:
            with atomic():
                # Note: bulk_create not supported for grandchild models, and is impossible under the time constraints
                for person_contact in person_contacts:
                    person_contact.user_id = person_contact.user.id
                    person_contact.save()
        except Exception as e:
            print(f"failed to create person contacts: {e.args[0]}")

        if "qa" not in self.origin:
            stripe_ids = {}
            for sc in stripe_customers:
                # First, django has an issue resolved like 4 months ago where, when bulk_creating a dependent object,
                # the object_id is left null even though the object is there
                # (https://code.djangoproject.com/ticket/29497)
                # so it has to be explicitly provided.
                sc.contact_id = sc.contact.contact_ptr_id
                # Second, there is a data integrity issue in firebase. Multiple customers share a stripe id,
                # which Stripe docs say is supposed to be unique. No idea which one is correct, so print a message
                # to let a human look at it if necessary. At any rate, don't crash because of the unique constraint.
                if stripe_ids.get(sc.stripe_id):
                    print(
                        f"Duplicate stripe customer {sc.stripe_id}. Stripe Contact {stripe_ids[sc.stripe_id].contact} "
                        f"will be replaced by Contact {sc.contact}"
                    )
                stripe_ids[sc.stripe_id] = sc
            try:
                StripeCustomer.objects.bulk_create(stripe_ids.values())
            except Exception as e:
                print("failed to create stripe_customers", e.args[0])
                return

        for vh in volunteer_hours:
            vh.donor_id = vh.donor.id
        try:
            VolunteerHours.objects.bulk_create(volunteer_hours)
        except Exception as e:
            print("failed to create volunteer_hours", e.args[0])
            return
        for opd in offplatform_donations:
            opd.donor_id = opd.donor.id
        try:
            OffPlatformDonation.objects.bulk_create(offplatform_donations)
        except Exception as e:
            print("failed to create offplatform_donations", e.args[0])
            return

    def _migrate_projects(self):  # noqa: C901

        existing_projects = {proj.name: proj for proj in Product.objects.all()}
        existing_charities = {
            vendor.name: vendor
            for vendor in Supplier.objects.filter(givesome_extra__vendor_type=VendorExtraType.CHARITY)
        }
        existing_categories = {cat.name: cat for cat in Category.objects.all()}
        # Note: some videos may have been entered by hand, so don't create doubles.
        existing_videos = {vid.video_id: vid for vid in CompletionVideo.objects.all()}

        tax_class = TaxClass.objects.filter(identifier="product").first()
        sales_unit = SalesUnit.objects.filter(identifier="pcs").first()

        projects = []
        product = (
            Product.objects.filter(sku__regex=r"^[0-9]+$")
            .annotate(sku_int=Cast("sku", IntegerField()))
            .order_by("-sku_int")
            .first()
        )
        sku = "0"
        if product is not None:
            sku = str(int(product.sku) + 1)
        project_extra = []
        shop_products = []
        categories = []
        videos = []
        stock_counts = []

        charities = []
        givesome_extra = []

        charity_shop_products = []

        for ref, project in self.givesome_data["projects"].items():
            if not existing_projects.get(project["headline"]):
                # Assume and hope that the manually entered name is the same as before.
                if not existing_charities.get(project["organization"]["name"]):
                    charity = Supplier(
                        name=project["organization"]["name"],
                        stock_managed=True,
                        module_identifier=settings.SHUUP_MULTIVENDOR_SUPPLIER_MODULE_IDENTIFIER,
                    )
                    url = project["organization"].get("link")[:128] if project["organization"].get("link") else None
                    givesome_extra.append(VendorExtra(allow_brand_page=False, vendor=charity, website_url=url))
                    charities.append(charity)
                    existing_charities[charity.name] = charity
                else:
                    charity = existing_charities[project["organization"]["name"]]

                identifier = "-".join(project["headline"].split(" "))
                givesome_project = Product(
                    shipping_mode=ShippingMode.NOT_SHIPPED,
                    tax_class=tax_class,
                    sales_unit=sales_unit,
                    description=project.get("description") or "",
                    name=project["headline"],
                    slug=identifier,
                    sku=sku,
                )
                raised = project.get("raised") or 0
                if project.get("fulfilled") and raised < project["goal"]:
                    # Project was closed out raise `raised` up to goal if needed
                    raised = project["goal"] if project["goal"] > raised else raised

                stock_counts.append(
                    StockCount(product=givesome_project, supplier=charity, logical_count=project["goal"] - raised)
                )
                project_extra.append(
                    ProjectExtra(
                        project=givesome_project,
                        goal_amount=project["goal"],
                        lives_impacted=project.get("people-impacted-count") or 0,
                        fully_funded_date=now() if project["goal"] <= raised else None,
                    )
                )
                shop_product = ShopProduct(
                    name=project["headline"],
                    description=project.get("description"),
                    default_price=TaxfulPrice(1, settings.SHUUP_HOME_CURRENCY),
                    product=givesome_project,
                    shop=self.main_shop,
                    visibility_limit=ProductVisibility.VISIBLE_TO_ALL,
                )
                charity_shop_products.append((charity, shop_product))

                if existing_categories.get(project.get("project-location")):
                    shop_product.primary_category = existing_categories[project["project-location"]]
                elif project.get("project-location"):
                    category = Category(name=project["project-location"])
                    existing_categories[category.name] = category
                    categories.append(category)
                    shop_product.primary_category = category

                self.projects[ref] = sku
                sku = str(int(sku) + 1)
                projects.append(givesome_project)

                if not existing_videos.get(project.get("video")) and project.get("video"):
                    video = CompletionVideo(
                        project=givesome_project,
                        url=f'https://www.youtube.com/embed/{project["video"]}?origin={self.origin}',
                    )
                    videos.append(video)

        try:
            with atomic():
                for project in projects:
                    project.save()
        except Exception as e:
            print(f"failed to create projects: {e.args[0]}")
            return

        try:
            for extra in project_extra:
                extra.project_id = extra.project.id
            ProjectExtra.objects.bulk_create(project_extra)
        except Exception as e:
            print(f"failed to create project extra: {e.args[0]}")
            return

        try:
            with atomic():
                # `bulk_create` skips over required steps like assigning `tree_id`. In this case, `tree_id` is the same
                for cat in categories:
                    # as `id`, which isn't known until after `bulk_create`.
                    cat.save()
                self.main_shop.categories.add(*categories)
        except Exception as e:
            print(f"failed to create categories: {e.args[0]}")
            return

        try:
            shop_products = [pair[1] for pair in charity_shop_products]
            with atomic():
                for sp in shop_products:
                    sp.product_id = sp.product.id
                    if sp.primary_category:
                        sp.primary_category_id = sp.primary_category.id
                    sp.save()
        except Exception as e:
            print(f"failed to create shop products: {e.args[0]}")
            return

        try:
            for vid in videos:
                vid.project_id = vid.project.id
            CompletionVideo.objects.bulk_create(videos)
        except Exception as e:
            print(f"failed to create categories: {e.args[0]}")
            return

        try:
            charities = Supplier.objects.bulk_create(charities)
            # Set M-N fields
            self.main_shop.suppliers.add(*charities)
            for charity, shop_product in charity_shop_products:
                shop_product.suppliers.add(charity)
                self.charities[shop_product.product.id] = charity
        except Exception as e:
            print(f"failed to create charities: {e.args[0]}")
            return

        try:
            SupplierPrice.objects.bulk_create(
                [
                    SupplierPrice(
                        shop=self.main_shop,
                        product=shop_product.product,
                        supplier=charity,
                        amount=TaxfulPrice(1, settings.SHUUP_HOME_CURRENCY),
                    )
                    for charity, shop_product in charity_shop_products
                ]
            )
        except Exception as e:
            print(f"failed to create supplier_prices: {e.args[0]}")
            return

        for stock in stock_counts:
            stock.product_id = stock.product.id
            stock.supplier_id = stock.supplier.id
        try:
            StockCount.objects.bulk_create(stock_counts)
        except Exception as e:
            print(f"failed to create stock counts: {e.args[0]}")
            return

        try:
            for extra in givesome_extra:
                extra.vendor_id = extra.vendor.id
            VendorExtra.objects.bulk_create(givesome_extra)
        except Exception as e:
            print(f"failed to create givesome extra: {e.args[0]}")
            return

    def _create_orders(self, firebase_donations, payment_method, orders, orderlines, ref_suffix, givesome_projects):
        complete = OrderStatus.objects.filter(identifier="complete").first()
        # firebase_key, person contact id
        users = {}
        with atomic():
            for firebase_key, username in self.users.items():
                users[firebase_key] = (
                    PersonContact.objects.filter(user__username=username).values_list("id", flat=True).first()
                )

        for ref, donation in firebase_donations.items():
            # Some missing data renders some donations impossible to migrate.
            # - Some donations are missing projects.
            # - There are donations referencing a project that does not exist in firebase (they seem to be test
            # donations).
            # - Multiple donations have no amount for what seems to be a variety of reasons.
            # - Log a reference in case there are questions.
            if not donation.get("project") or self.projects.get(donation.get("project")) is None:
                print(f"Donation is missing a project (ref {ref})")
                continue
            if not donation.get("amount"):
                print(f"Donation is missing an amount (ref {ref})")
                continue

            # There is at least one timestamp that resolves to year 52259 and raises a ValueError. O.o First 10
            # digits resolve to reasonable timeframes.
            timestamp = self._get_timestamp(donation["timestamp"])
            order = Order(
                reference_number=ref + ref_suffix,
                key=get_random_string(32),
                customer_id=users.get(donation.get("user")),
                order_date=timestamp,
                payment_date=timestamp,
                payment_method=payment_method,
                payment_status=PaymentStatus.FULLY_PAID,
                shop=self.main_shop,
                status=complete,
                taxless_total_price=TaxlessPrice(donation["amount"], settings.SHUUP_HOME_CURRENCY),
                prices_include_tax=False,
            )

            orderlines.append(
                OrderLine(
                    base_unit_price=TaxlessPrice(1, settings.SHUUP_HOME_CURRENCY),
                    quantity=donation["amount"],
                    product_id=givesome_projects[donation["project"]],
                    supplier=self.charities[givesome_projects[donation["project"]]],
                    created_on=timestamp,
                    order=order,
                )
            )
            orderlines.append(OrderLine(quantity=1, type=OrderLineType.PAYMENT, created_on=timestamp, order=order))
            orders.append(order)

            if "card" in donation:
                # Map givecard codes to order references for later
                self.donations[donation["card"]] = ref

    def _migrate_donations(self):
        orders = []
        orderlines = []
        # firebase_key, product id
        givesome_project_ids = {}
        with atomic():
            for firebase_key, sku in self.projects.items():
                givesome_project_ids[firebase_key] = (
                    Product.objects.filter(sku=sku).values_list("id", flat=True).first()
                )

        payment_method = PaymentMethod.objects.filter(
            payment_processor=StripeMultivendorPaymentProcessor.objects.filter(enabled=True).first()
        ).first()
        self._create_orders(
            self.givesome_data["cash-donations"], payment_method, orders, orderlines, "-s", givesome_project_ids
        )

        payment_method = PaymentMethod.objects.filter(
            payment_processor=GivecardPaymentProcessor.objects.filter(enabled=True).first()
        ).first()
        self._create_orders(
            self.givesome_data["givecard-donations"], payment_method, orders, orderlines, "-g", givesome_project_ids
        )

        order_ids = set()
        try:
            print("Migrating and backdating orders")
            for order in orders:
                order.save()
                order.created_on = order.payment_date
                order.identifier = order.id
                order.save()
        except Exception as e:
            print(f"failed to create orders: {e.args[0]}")
            import traceback

            traceback.print_exc()
            return
        for line in orderlines:
            line.order_id = line.order.id
            order_ids.add(line.order.id)
        try:
            print("Migrating and backdating orderlines")
            for line in orderlines:
                line.save()
                line.created_on = line.order.created_on
                line.save()
        except Exception as e:
            print(f"failed to create orderlines: {e.args[0]}")
            import traceback

            traceback.print_exc()
            return

        try:
            for order in orders:
                payment = Payment.objects.create(
                    payment_identifier=f"{order.id}:1",
                    amount_value=order.taxless_total_price_value,
                    description=_(f"Migrated Payment for Donation # {order.id}"),
                    order_id=order.id,
                )
                payment.created_on = payment.order.created_on
                payment.save()

        except Exception as e:
            print(f"failed to create payments: {e.args[0]}")
            return

    @staticmethod
    def _get_redeemed_by(redeemer: dict):
        try:
            return redeemer.get("redeemed-by")
        except AttributeError as ae:
            print(f"Redeemer information is in the wrong format: {type(redeemer)}, {ae.args[0]}")

    def _card_is_importable(self, card_data, code):
        """Multicards and givecards that have been redeemed and not spent are potentially importable."""
        if "multi-use" in card_data:
            # multicard
            if not card_data.get("redeemed-group"):
                # Nobody has this card on their account
                return card_data["expires"] > now().timestamp()
            else:
                # somebody has redeemed at least one card
                use_count = card_data["use-count"]
                for redeemer in card_data["redeemed-group"].values():
                    val = _get_givecard_balance(self.givesome_data, self._get_redeemed_by(redeemer), code)
                    if val > 0:
                        # At least one multicard has been redeemed and not spent, and is sitting in the user's account.
                        return True
                return use_count > len(card_data["redeemed-group-list"]) and card_data["expires"] > now().timestamp()
        else:
            if not card_data.get("redeemed"):
                # Not redeemed at all, so check if the card is expired.
                return card_data["expires"] > now().timestamp()
            else:
                # Redeemed, so see if there is a balance left.
                return _get_givecard_balance(self.givesome_data, card_data.get("redeemed-by"), code) > 0

    def _create_multicard_cards(self, code, card_data, batch, users):
        """Create mulitcard cards if they are unredeemed, or redeemed but unspent."""
        cards = []
        redeemed_count = 0
        if "redeemed-group-list" in card_data:
            redeemed_count = len(card_data["redeemed-group-list"])
            for user in card_data["redeemed-group"].values():
                user_key = self._get_redeemed_by(user)
                if user_key is not None:
                    balance = _get_givecard_balance(self.givesome_data, user_key, code)
                    if balance > 0:
                        cards.append(
                            Givecard(
                                user_id=users.get(user_key),
                                balance=balance,
                                batch=batch,
                                redeemed_on=self._get_timestamp(user["redeemed-date"]),
                            )
                        )
        unredeemed = card_data["use-count"] - redeemed_count
        cards += [Givecard(balance=card_data["value"], batch=batch) for __ in range(unredeemed)]
        return cards

    def _create_batch(self, card, code, supplier):
        expiration_date = self._get_timestamp(card["expires"])
        if supplier is None:
            expiration_date = self.final_expiration

        return GivecardBatch(
            restriction_type=GivecardDonateRestrictionType.DISABLED,
            supplier=supplier,
            expiration_date=expiration_date,
            expiry_type=GivecardBatchExpiryType.DISABLED,
            amount=1,  # <-- just a required placeholder for now. Need to count actual givecards imported.
            value=card["value"],
            code=code if "multi-use" in card else None,
        )

    @staticmethod
    def _get_earliest_redemption(givecards):
        """Dermine the earliest date any of these givecards were redeemed, if applicable"""
        unredeemed = [card for card in givecards if card.redeemed_on is None]
        if len(unredeemed) < len(givecards):
            redeemed = [card for card in givecards if card.redeemed_on is not None]
            earliest = min(redeemed, key=lambda card: card.redeemed_on)
            return earliest.redeemed_on

    def _migrate_givecards(self):  # noqa: C901
        """Invert the givecard data from its old firebase structure to its new shuup structure."""
        campaigns: Dict[str, GivecardCampaign] = {}
        batches: Dict[str, GivecardBatch] = {}  # expiry_date + campaign identifier, batch object
        batches_of_cards: Dict[str, List[Givecard]] = {}  # i.e. expiry_date + campaign identifier, list of instances
        identifier = 0
        # firebase_key, user id
        users = {}
        with atomic():
            for firebase_key, username in self.users.items():
                users[firebase_key] = User.objects.filter(username=username).values_list("id", flat=True).first()

        vendors: Dict[str, Supplier] = {
            vendor.name: vendor
            for vendor in Supplier.objects.filter(givesome_extra__vendor_type=VendorExtraType.BRANDED_VENDOR)
        }

        for code, card in self.givesome_data["givecards"]["cards"].items():
            if self._card_is_importable(card, code):
                campaign_key = card.get("entity")
                if not campaign_key:
                    print(f"{code} has no campaign key.")
                    campaign_key = str(identifier)
                    identifier += 1
                batch_key = "-".join([str(card["expires"]), campaign_key])
                supplier = None

                if not batches.get(batch_key):
                    try:
                        vendor_name = self.givesome_data["givecards"]["entities"][campaign_key]["name"]
                    except KeyError:
                        # Data is missing. One more thing to try.
                        try:
                            vendor_name = self.givesome_data["skins"][card["skin"]]["name"]
                        except KeyError:
                            # Cannot determine vendor
                            vendor_name = None

                    supplier = vendors.get(vendor_name)
                    batch = self._create_batch(card, code, supplier)
                    if batch is None:
                        continue
                    batches[batch_key] = batch
                    batches_of_cards[batch_key] = []

                campaign = campaigns.get(campaign_key)
                if card.get("entity") and campaign is None:
                    firebase_campaign = self.givesome_data["givecards"]["entities"].get(campaign_key)
                    if firebase_campaign:
                        campaign = GivecardCampaign(
                            identifier=campaign_key,
                            name=" ".join(re.split("-|_", campaign_key)),
                            supplier=supplier,
                            message=firebase_campaign["message"],
                        )
                if campaign is not None:
                    batches[batch_key].campaign = campaign
                    campaigns[campaign_key] = campaign

                cards = []
                if "multi-use" not in card:
                    # normal individual Givecard
                    user_key = card.get("redeemed-by")
                    if user_key:
                        redeemer_id = users.get(user_key)
                        balance = _get_givecard_balance(self.givesome_data, user_key, code)
                        if balance > 0 and redeemer_id is not None:
                            # Card is spendable and accessible
                            cards.append(
                                Givecard(
                                    user_id=redeemer_id,
                                    code=code,
                                    balance=balance,
                                    batch=batches[batch_key],
                                    redeemed_on=self._get_timestamp(card.get("redeemed-date")),
                                )
                            )
                else:
                    # multicard
                    cards = self._create_multicard_cards(code, card, batches[batch_key], users)
                batches_of_cards[batch_key] += cards

        try:
            # There is at least one campaign that has only batches with only unimportable givecards.
            with atomic():
                for campaign in campaigns.values():
                    campaign.save()
        except Exception as e:
            print(f"failed to create campaigns: {e.args[0]}")

        try:
            with atomic():
                for batch_key, batch in batches.items():
                    # Fill in missing attributes (amount and generated_on)
                    batch.amount = len([card for card in batches_of_cards[batch_key]])
                    if batch.amount:
                        # Extend expiration to August 2021 to give redeemers one last chance to donate.
                        # Also don't keep batches with no givecards.
                        batch.expiration_date = self.final_expiration
                        batch.generated_on = self._get_earliest_redemption(batches_of_cards[batch_key]) or now()
                        if batch.campaign:
                            batch.campaign_id = batch.campaign.id
                        batch.save()
        except Exception as e:
            print(f"failed to create batches: {e.args[0]}")

        try:
            # Backdate campaigns to the earliest batch generated.
            # OuterRef/Subquery keeps failing complaining about null required values, so atomic it is.
            with atomic():
                for campaign in campaigns.values():
                    earliest = campaign.batches.order_by("generated_on").first()
                    if earliest:
                        campaign.created_on = earliest.generated_on
                        campaign.save()
        except Exception as e:
            print(f"failed to backdate campaigns.: {e.args[0]}")

        cards = [givecard for batch in batches_of_cards.values() for givecard in batch]
        for card in cards:
            card.batch_id = card.batch.id
        try:
            Givecard.objects.bulk_create(cards, batch_size=self.limit)
        except Exception as e:
            print(f"failed to create Givecards: {e.args[0]}")

    def _migrate(self):
        global models
        existing = {model.__name__: model.objects.all().values_list("id", flat=True) for model in models}
        try:
            self._migrate_users()
            self._migrate_projects()
            self._migrate_donations()
            self._migrate_givecards()
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(e.args[0])
            cleanup(existing)

    def handle(self, *args, **options):
        """This command uses the firebase Python sdk, which looks for a GOOGLE_APPLICATION_CREDENTIALS environment
        variable containing the path to the Givesome firebase project json credentials.

        A required "--path" option should contain the path to the exported data.

        E.g. migrate_givesome_data --path /path/to/data.json

        If migrating to a target other than givesome.shuup.com, please include the target scheme and domain.

        E.g. migrate_givesome_data --path /path/to/creds.json --origin https://givesome-qa.shuup.com

        """
        from django.utils.timezone import localtime

        now = localtime()
        activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)
        self.main_shop = Shop.objects.first()
        self.origin = options["origin"]

        try:
            with open(options["path"]) as file:
                self.givesome_data = file.read()
                self.givesome_data = json.loads(self.givesome_data)
        except FileNotFoundError:
            print("File not found. Please check your path and filename.")

        self._migrate()

        print(localtime() - now)

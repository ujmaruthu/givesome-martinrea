# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core.management import BaseCommand, call_command
from django.utils.translation import activate
from shuup import configuration
from shuup.core.defaults.order_statuses import create_default_order_statuses
from shuup.core.models import (
    ConfigurationItem,
    Currency,
    ProductType,
    SalesUnit,
    Shop,
    ShopStatus,
    Supplier,
    SupplierShop,
    TaxClass,
    get_person_contact,
)
from shuup.front.checkout.methods import SHIPPING_METHOD_REQUIRED_CONFIG_KEY
from shuup.xtheme import get_current_theme, set_current_theme
from shuup_multivendor.models import SupplierUser
from shuup_multivendor.utils.configuration import set_product_tax_class_options, set_shipping_method_tax_class_options
from shuup_multivendor.utils.funds import set_vendor_default_revenue_percentage

from givesome.admin_module.forms.shop_settings import get_donation_amount_options
from givesome.enums import VendorExtraType
from givesome.models import GivesomePurse, ReceiptingMessages, VendorExtra


class Command(BaseCommand):
    def add_arguments(self, parser):  # python manage.py init_project --create_vendors 1
        parser.add_argument("--create_vendors", type=int, required=False, help="Create and .")

    def create_supplier(self, name, vendor_name, main_shop):
        vendor_user, vendor_user_created = User.objects.get_or_create(
            username=name,
            defaults=dict(
                email=f"{name}@example.com",
                first_name="First",
                last_name=f"{name.capitalize()}",
                is_staff=True,
                is_active=True,
            ),
        )
        if vendor_user_created:
            vendor_user.set_password(name)
            vendor_user.save()
            print(f"{name} user created.")

        vendor, __ = Supplier.objects.get_or_create(
            identifier=f"{vendor_name}-vendor", defaults=dict(name=f"{vendor_name.capitalize()} Vendor", enabled=True)
        )
        SupplierShop.objects.update_or_create(shop=main_shop, supplier=vendor, defaults={"is_approved": True})
        SupplierUser.objects.get_or_create(shop=main_shop, supplier=vendor, user=vendor_user)
        contact = get_person_contact(vendor_user)
        contact.shops.set([main_shop])

        return vendor_user, vendor

    def handle(self, *args, **options):
        activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)

        create_default_order_statuses()

        ProductType.objects.update_or_create(identifier="default", defaults=dict(name="Standard Product"))
        SalesUnit.objects.update_or_create(identifier="pcs", defaults=dict(name="Pieces", symbol="pcs"))
        product_tax = TaxClass.objects.update_or_create(identifier="product", defaults=dict(name="Product Tax Class"))
        shipping_tax = TaxClass.objects.update_or_create(
            identifier="shipping", defaults=dict(name="Shipping Tax Class")
        )
        TaxClass.objects.update_or_create(identifier="payment", defaults=dict(name="Payment Tax Class"))

        Currency.objects.get_or_create(code="CAD")

        # Create main shop
        main_shop, __ = Shop.objects.get_or_create(
            identifier="givesome",
            defaults=dict(
                name="Givesome",
                public_name="Givesome",
                domain="givesome",
                currency="CAD",
                maintenance_mode=False,
                status=ShopStatus.ENABLED,
            ),
        )
        GivesomePurse.objects.get_or_create(shop=main_shop, supplier=None)

        if not get_current_theme(main_shop):
            set_current_theme("givesome", main_shop)

        if not configuration.get(main_shop, "multivendor_product_tax_class_options"):
            set_product_tax_class_options(main_shop, [product_tax[0]])

        if not configuration.get(main_shop, "multivendor_shipping_method_tax_class_options"):
            set_shipping_method_tax_class_options(main_shop, [shipping_tax[0]])

        # Vendors receive 100% of sales
        set_vendor_default_revenue_percentage(main_shop, 100)

        # Disable shipping method requirement in checkout
        configuration.set(main_shop, SHIPPING_METHOD_REQUIRED_CONFIG_KEY, False)

        main_site = Site.objects.first()
        if not main_site:
            main_site = Site()

        if main_site:
            main_site.name = main_shop.public_name[:50]
            main_site.domain = main_shop.domain
            main_site.save()

        # Create admin user
        admin_user, admin_created = User.objects.get_or_create(
            username="admin",
            defaults=dict(
                email="admin@example.com",
                first_name="Admin",
                last_name="Superuser",
                is_staff=True,
                is_active=True,
                is_superuser=True,
            ),
        )
        if admin_created:
            admin_user.set_password("admin")
            admin_user.save()

        staff, staff_created = User.objects.get_or_create(
            username="staff",
            defaults=dict(
                email="staff@example.com", first_name="First", last_name="Staff", is_staff=True, is_active=True
            ),
        )
        if staff_created:
            staff.set_password("staff")
            staff.save()

        main_shop.staff_members.add(staff)

        # Set up permission groups
        staff_group, __ = Group.objects.get_or_create(name=settings.STAFF_PERMISSION_GROUP_NAME)
        staff_menu_group, __ = Group.objects.get_or_create(name="Staff Menu Edit Permissions")

        vendor_group, __ = Group.objects.get_or_create(name=settings.VENDORS_PERMISSION_GROUP_NAME)
        vendor_menu_group, __ = Group.objects.get_or_create(name="Vendor Menu Edit Permissions")

        charity_group, __ = Group.objects.get_or_create(name="Charity")
        brand_group, __ = Group.objects.get_or_create(name="Brand")

        configuration.set(main_shop, "staff_user_permission_group", staff_group.pk)
        configuration.set(main_shop, "vendor_user_permission_group", vendor_group.pk)

        # Staff permissions
        staff.groups.add(staff_group)
        staff.groups.add(staff_menu_group)

        if options["create_vendors"]:
            # Create vendor users and suppliers
            vendor_user, vendor = self.create_supplier("vendor", "givesome", main_shop)
            charity_user, charity_vendor = self.create_supplier("charity", "charity", main_shop)
            brand_user, brand_vendor = self.create_supplier("brand", "brand", main_shop)

            # Create vendor_extras for vendors
            VendorExtra.objects.get_or_create(
                vendor=vendor, defaults=dict(vendor_type=VendorExtraType.CHARITY, allow_brand_page=True)
            )
            VendorExtra.objects.get_or_create(
                vendor=charity_vendor, defaults=dict(vendor_type=VendorExtraType.CHARITY, allow_brand_page=False)
            )
            VendorExtra.objects.get_or_create(
                vendor=brand_vendor, defaults=dict(vendor_type=VendorExtraType.BRANDED_VENDOR, allow_brand_page=True)
            )

            # Permissions
            vendor_user.groups.add(vendor_group)
            vendor_user.groups.add(vendor_menu_group)
            # Givesome vendor needs to be in brand and charity group, to edit supplier menu
            vendor_user.groups.add(brand_group)
            vendor_user.groups.add(charity_group)

            charity_user.groups.add(vendor_group)
            charity_user.groups.add(charity_group)
            brand_user.groups.add(vendor_group)
            brand_user.groups.add(brand_group)

        # Configure pre-determined donation amounts if needed.
        donation_options = get_donation_amount_options(main_shop)
        if donation_options.count() == 0:
            ops = [2, 5, 10]
            ConfigurationItem.objects.bulk_create(
                [
                    ConfigurationItem(
                        key="givesome_donation_amount_options_{}".format(str(amt)), shop=main_shop, value=amt
                    )
                    for amt in ops
                ]
            )

        messages = ReceiptingMessages.objects.all()
        if messages.count() == 0:
            ReceiptingMessages.objects.create(
                welcome="Receipting now available for qualifying donations - look for the receipting symbol.",
                project_card="You may be eligible to receive an annual tax receipt for any donations made to this "
                "project.",
                charity_page="You may be eligible to receive an annual tax receipt for any donations made to this "
                "charity if your cumulative donations in a year are $20 or more.",
                project_page="You may be eligible to receive an annual tax receipt for any donations made to this "
                "project. Donations made with Givecard PINs are not eligible for tax receipts.",
                checkout_no="I do not wish to share my information to get a tax receipt",
                checkout_yes="Yes, I would like to receive a tax receipt from the charity for this donation that I "
                "am making to CHARITY_NAME, registration # REGISTRATION_NUMBER, and understand my "
                "information will be shared with the charity",
                checkout_warn="Oops – to be eligible to receive tax receipts you need to log in, set up an account "
                "profile or complete your profile information.",
                checkout_givecard="Donations made with Givecards/PINs are not eligible for tax receipts.",
                portfolio="Your full name is required for tax receipting purposes.",
            )
        else:
            message = messages.first()
            if message.sign_in_header == "":
                message.sign_in_header = "COMPLETE YOUR ACCOUNT TO RECEIVE TAX RECEIPTS."
                message.sign_in_step_1 = (
                    "Click the link in your verification email (a new browser will open confirming your email has "
                    "been verified)."
                )
                message.sign_in_step_2 = 'Return to this page and click "sign in" in the top right of your screen.'
                message.sign_in_step_3 = "Complete your user profile. Don't forget to click save!"
                message.save()

        call_command("populate_exchange_rate_sources")

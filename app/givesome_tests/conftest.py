# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from collections import namedtuple

import pytest
from django.conf import settings
from django.core.signals import setting_changed
from shuup.apps.provides import clear_provides_cache
from shuup.core.models import ShippingMode, Supplier, SupplierModule, get_person_contact
from shuup.testing import factories
from shuup.testing.factories import get_default_shop
from shuup.utils.importing import clear_load_cache
from shuup.xtheme.testing import override_current_theme_class
from shuup_multivendor.models import SupplierUser

from givesome.enums import VendorExtraType
from givesome.models import GivesomeOffice, ProjectExtra, VendorExtra


def clear_caches(setting, **kwargs):
    clear_load_cache()
    if setting == "INSTALLED_APPS":
        clear_provides_cache()


def pytest_configure(config):
    setting_changed.connect(clear_caches, dispatch_uid="shuup_test_clear_caches")
    settings.SHUUP_TELEMETRY_ENABLED = False


def pytest_runtest_call(item):
    # All tests are run with a theme override `shuup.themes.classic_gray.ClassicGrayTheme`.
    # To un-override, use `with override_current_theme_class()` (no arguments to re-enable database lookup)
    from shuup.themes.classic_gray.theme import ClassicGrayTheme

    item.session._theme_overrider = override_current_theme_class(ClassicGrayTheme, get_default_shop())
    item.session._theme_overrider.__enter__()


def pytest_runtest_teardown(item, nextitem):
    if hasattr(item.session, "_theme_overrider"):
        item.session._theme_overrider.__exit__(None, None, None)
        del item.session._theme_overrider


@pytest.fixture(scope="session")
def splinter_make_screenshot_on_failure():
    return False


# use django_db on every test
# activate the EN language by default
# initialize a new cache
@pytest.fixture(autouse=True)
def enable_db_access(db):
    from django.utils.translation import activate

    activate("en")

    # make sure the default cache is also cleared
    # it is used by third party apps like parler
    from django.core.cache import cache

    cache.clear()

    from shuup.core import cache

    cache.init_cache()

    from shuup import configuration
    from shuup.core.setting_keys import (
        SHUUP_ALLOW_ANONYMOUS_ORDERS,
        SHUUP_DEFAULT_ORDER_LABEL,
        SHUUP_REFERENCE_NUMBER_METHOD,
        SHUUP_TAX_MODULE,
    )

    configuration.set(None, SHUUP_ALLOW_ANONYMOUS_ORDERS, True)
    configuration.set(None, SHUUP_DEFAULT_ORDER_LABEL, "default")
    configuration.set(None, SHUUP_REFERENCE_NUMBER_METHOD, "unique")
    configuration.set(None, SHUUP_TAX_MODULE, "default_tax")


@pytest.fixture()
def vendor_user_charity(db, django_user_model, django_username_field):
    vd = _create_vendor_user("charity", django_user_model)
    VendorExtra.objects.get_or_create(vendor=vd.vendor, vendor_type=VendorExtraType.CHARITY, allow_brand_page=False)

    p1 = _create_project_for_charity(vd.vendor, "sku-1", 1)
    p2 = _create_project_for_charity(vd.vendor, "sku-2", 1)
    p3 = _create_project_for_charity(vd.vendor, "sku-3", 1)
    p4 = _create_project_for_charity(vd.vendor, "sku-4", 1)

    CharityData = namedtuple("CharityData", "user vendor project project2 project3 project4 all_projects")
    return CharityData(vd.user, vd.vendor, p1, p2, p3, p4, [p1, p2, p3, p4])


@pytest.fixture()
def vendor_user_brand(db, django_user_model, django_username_field):
    vd = _create_vendor_user("brand", django_user_model)
    VendorExtra.objects.get_or_create(
        vendor=vd.vendor, vendor_type=VendorExtraType.BRANDED_VENDOR, allow_brand_page=True
    )
    o1 = GivesomeOffice.objects.create(supplier=vd.vendor, name="Office1")
    o2 = GivesomeOffice.objects.create(supplier=vd.vendor, name="Office2")
    o3 = GivesomeOffice.objects.create(supplier=vd.vendor, name="Office3")

    BrandData = namedtuple("BrandData", "user vendor office office2 office3")
    return BrandData(vd.user, vd.vendor, o1, o2, o3)


@pytest.fixture()
def vendor_user_brand_2(db, django_user_model, django_username_field):
    vd = _create_vendor_user("brand_2", django_user_model)
    VendorExtra.objects.get_or_create(
        vendor=vd.vendor, vendor_type=VendorExtraType.BRANDED_VENDOR, allow_brand_page=True
    )
    o1 = GivesomeOffice.objects.create(supplier=vd.vendor, name="Chapter1")
    o2 = GivesomeOffice.objects.create(supplier=vd.vendor, name="Chapter2")
    o3 = GivesomeOffice.objects.create(supplier=vd.vendor, name="Chapter3")

    BrandData = namedtuple("BrandData", "user vendor office office2 office3")
    return BrandData(vd.user, vd.vendor, o1, o2, o3)


def _create_vendor_user(username, django_user_model):
    user, __ = django_user_model.objects.get_or_create(
        username=f"{username}-user",
        defaults=dict(
            email=f"{username}@example.com",
            first_name="First",
            last_name=f"{username.capitalize()}",
            is_staff=True,
            is_active=True,
        ),
    )
    user.set_password(username)
    user.save()

    get_person_contact(user)

    shop = factories.get_default_shop()
    vendor = Supplier.objects.create(
        identifier=f"{username}-vendor",
        name=f"{username.capitalize()} Vendor",
        enabled=True,
    )
    vendor.supplier_modules.add(SupplierModule.objects.get(module_identifier="simple_supplier"))
    vendor.shops.add(shop)
    SupplierUser.objects.create(shop=shop, supplier=vendor, user=user)

    VendorData = namedtuple("VendorData", "user vendor")
    vd = VendorData(user, vendor)
    return vd


def _create_project_for_charity(supplier, sku, price):
    shop = factories.get_default_shop()
    product = factories.create_product(sku, shop, supplier=supplier, default_price=price)
    product.shipping_mode = ShippingMode.NOT_SHIPPED
    product.save()
    shop_product = product.get_shop_instance(shop)

    ProjectExtra.objects.create(project=product, goal_amount=1000)
    supplier.adjust_stock(shop_product.id, 1000)
    return shop_product

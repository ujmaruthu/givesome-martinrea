# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from shuup_workbench.settings.utils import get_disabled_migrations
from shuup_workbench.test_settings import *  # noqa

INSTALLED_APPS = list(locals().get("INSTALLED_APPS", [])) + [
    "givesome",
    "shuup_multivendor",
    "shuup_stripe_multivendor",  # Causes importing errors if this is not installed
    "shuup_subscriptions",  # Causes importing errors if this is not installed
    "shuup_firebase_auth",  # Causes importing errors if this is not installed
    "shuup_api",  # Causes importing errors if this is not installed
    "django.contrib.sites",  # Causes importing errors if this is not installed
    "shuup_multicurrencies_display",  # Causes importing errors if this is not installed
]

# DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "test_db.sqlite3"}}

MIGRATION_MODULES = get_disabled_migrations()
MIGRATION_MODULES.update({app: None for app in INSTALLED_APPS})

ROOT_URLCONF = "givesome_tests.urls"

SHUUP_MULTIVENDOR_SUPPLIER_STOCK_MANAGED_BY_DEFAULT = True
SHUUP_MULTIVENDOR_ENABLE_CUSTOM_PRODUCTS = True
VENDOR_CAN_SHARE_PRODUCTS = False
SHUUP_ORDER_SOURCE_MODIFIER_MODULES = []
SHUUP_ALLOW_ANONYMOUS_ORDERS = True

SHUUP_ADMIN_SUPPLIER_PROVIDER_SPEC = "shuup_multivendor.supplier_provider.MultivendorSupplierProvider"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("shuup_api.permissions.ShuupAPIPermission",),
}

GIVESOME_MULTICARD_REDEEM_GRACE_PERIOD_DAYS = 123

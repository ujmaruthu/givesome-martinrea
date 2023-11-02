# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.conf import settings

from shuup import configuration
from shuup.admin.setting_keys import (
    SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION,
    SHUUP_ADMIN_ALLOW_HTML_IN_SUPPLIER_DESCRIPTION,
)
from shuup.core.constants import DEFAULT_REFERENCE_NUMBER_LENGTH
from shuup.core.setting_keys import (
    SHUUP_ADDRESS_HOME_COUNTRY,
    SHUUP_ALLOW_ANONYMOUS_ORDERS,
    SHUUP_ALLOW_ARBITRARY_REFUNDS,
    SHUUP_ALLOW_EDITING_ORDER,
    SHUUP_ALLOWED_UPLOAD_EXTENSIONS,
    SHUUP_CALCULATE_TAXES_AUTOMATICALLY_IF_POSSIBLE,
    SHUUP_DEFAULT_ORDER_LABEL,
    SHUUP_DISCOUNT_MODULES,
    SHUUP_ENABLE_ATTRIBUTES,
    SHUUP_ENABLE_MULTIPLE_SHOPS,
    SHUUP_ENABLE_MULTIPLE_SUPPLIERS,
    SHUUP_HOME_CURRENCY,
    SHUUP_LENGTH_UNIT,
    SHUUP_MANAGE_CONTACTS_PER_SHOP,
    SHUUP_MASS_UNIT,
    SHUUP_MAX_UPLOAD_SIZE,
    SHUUP_ORDER_SOURCE_MODIFIER_MODULES,
    SHUUP_PRICING_MODULE,
    SHUUP_REFERENCE_NUMBER_LENGTH,
    SHUUP_REFERENCE_NUMBER_METHOD,
    SHUUP_REFERENCE_NUMBER_PREFIX,
    SHUUP_TAX_MODULE,
    SHUUP_TELEMETRY_ENABLED,
    SHUUP_VOLUME_UNIT,
)
from shuup.front.setting_keys import (
    SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD,
    SHUUP_FRONT_MAX_UPLOAD_SIZE,
    SHUUP_REGISTRATION_REQUIRES_ACTIVATION,
)
from shuup.reports.constants import DEFAULT_REPORTS_ITEM_LIMIT
from shuup.reports.setting_keys import SHUUP_DEFAULT_REPORTS_ITEM_LIMIT
from shuup.testing.factories import get_currency


def populate_configuration():
    get_currency("EUR", 2)
    configuration.set(None, SHUUP_HOME_CURRENCY, getattr(settings, "SHUUP_HOME_CURRENCY", "EUR"))
    configuration.set(None, SHUUP_ADDRESS_HOME_COUNTRY, getattr(settings, "SHUUP_ADDRESS_HOME_COUNTRY", None))
    configuration.set(None, SHUUP_ALLOW_ANONYMOUS_ORDERS, getattr(settings, "SHUUP_ALLOW_ANONYMOUS_ORDERS", True))
    configuration.set(None, SHUUP_REFERENCE_NUMBER_METHOD, getattr(settings, "SHUUP_REFERENCE_NUMBER_METHOD", "unique"))
    configuration.set(
        None,
        SHUUP_REFERENCE_NUMBER_LENGTH,
        getattr(settings, "SHUUP_REFERENCE_NUMBER_LENGTH", DEFAULT_REFERENCE_NUMBER_LENGTH),
    )
    configuration.set(None, SHUUP_REFERENCE_NUMBER_PREFIX, getattr(settings, "SHUUP_REFERENCE_NUMBER_PREFIX", ""))
    configuration.set(
        None,
        SHUUP_DISCOUNT_MODULES,
        getattr(settings, "SHUUP_DISCOUNT_MODULES", ["customer_group_discount", "product_discounts"]),
    )
    configuration.set(None, SHUUP_PRICING_MODULE, getattr(settings, "SHUUP_PRICING_MODULE", "customer_group_pricing"))
    configuration.set(
        None,
        SHUUP_ORDER_SOURCE_MODIFIER_MODULES,
        getattr(settings, "SHUUP_ORDER_SOURCE_MODIFIER_MODULES", ["basket_campaigns"]),
    )
    configuration.set(None, SHUUP_TAX_MODULE, getattr(settings, "SHUUP_TAX_MODULE", "default_tax"))
    configuration.set(None, SHUUP_ENABLE_ATTRIBUTES, getattr(settings, "SHUUP_ENABLE_ATTRIBUTES", True))
    configuration.set(None, SHUUP_ENABLE_MULTIPLE_SHOPS, getattr(settings, "SHUUP_ENABLE_MULTIPLE_SHOPS", False))
    configuration.set(
        None, SHUUP_ENABLE_MULTIPLE_SUPPLIERS, getattr(settings, "SHUUP_ENABLE_MULTIPLE_SUPPLIERS", False)
    )
    configuration.set(None, SHUUP_MANAGE_CONTACTS_PER_SHOP, getattr(settings, "SHUUP_MANAGE_CONTACTS_PER_SHOP", False))
    configuration.set(None, SHUUP_ALLOW_EDITING_ORDER, getattr(settings, "SHUUP_ALLOW_EDITING_ORDER", True))
    configuration.set(None, SHUUP_DEFAULT_ORDER_LABEL, getattr(settings, "SHUUP_DEFAULT_ORDER_LABEL", "default"))
    configuration.set(None, SHUUP_TELEMETRY_ENABLED, getattr(settings, "SHUUP_TELEMETRY_ENABLED", False))
    configuration.set(
        None,
        SHUUP_CALCULATE_TAXES_AUTOMATICALLY_IF_POSSIBLE,
        getattr(settings, "SHUUP_CALCULATE_TAXES_AUTOMATICALLY_IF_POSSIBLE", True),
    )
    configuration.set(None, SHUUP_ALLOW_ARBITRARY_REFUNDS, getattr(settings, "SHUUP_ALLOW_ARBITRARY_REFUNDS", True))
    configuration.set(
        None,
        SHUUP_ALLOWED_UPLOAD_EXTENSIONS,
        getattr(settings, "SHUUP_ALLOWED_UPLOAD_EXTENSIONS", ["pdf", "ttf", "eot", "woff", "woff2", "otf"]),
    )
    configuration.set(None, SHUUP_MAX_UPLOAD_SIZE, getattr(settings, "SHUUP_MAX_UPLOAD_SIZE", 5000000))
    configuration.set(None, SHUUP_MASS_UNIT, getattr(settings, "SHUUP_MASS_UNIT", "g"))
    configuration.set(None, SHUUP_LENGTH_UNIT, getattr(settings, "SHUUP_LENGTH_UNIT", "mm"))
    configuration.set(None, SHUUP_VOLUME_UNIT, "{}3".format(getattr(settings, "SHUUP_LENGTH_UNIT", "mm3")))

    configuration.set(
        None,
        SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION,
        getattr(settings, "SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION", True),
    )
    configuration.set(
        None,
        SHUUP_ADMIN_ALLOW_HTML_IN_SUPPLIER_DESCRIPTION,
        getattr(settings, "SHUUP_ADMIN_ALLOW_HTML_IN_VENDOR_DESCRIPTION", True),
    )
    configuration.set(None, SHUUP_FRONT_MAX_UPLOAD_SIZE, getattr(settings, "SHUUP_FRONT_MAX_UPLOAD_SIZE", 500000))
    configuration.set(
        None,
        SHUUP_DEFAULT_REPORTS_ITEM_LIMIT,
        getattr(settings, "DEFAULT_REPORTS_ITEM_LIMIT", DEFAULT_REPORTS_ITEM_LIMIT),
    )
    configuration.set(None, SHUUP_REGISTRATION_REQUIRES_ACTIVATION, False)
    configuration.set(None, SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD, False)

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import django.conf

from shuup.apps import AppConfig
from shuup.core.excs import MissingSettingException
from shuup.utils import money


class ShuupCoreAppConfig(AppConfig):
    name = "shuup.core"
    verbose_name = "Shuup Core"
    label = "shuup"  # Use "shuup" as app_label instead of "core"
    required_installed_apps = (
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "easy_thumbnails",
        "filer",
    )
    provides = {
        "pricing_module": ["shuup.core.pricing.default_pricing:DefaultPricingModule"],
        "order_source_validator": [
            "shuup.core.order_creator:OrderSourceMinTotalValidator",
            "shuup.core.order_creator:OrderSourceMethodsUnavailabilityReasonsValidator",
            "shuup.core.order_creator:OrderSourceSupplierValidator",
        ],
        "product_kind_specs": ["shuup.core.specs.product_kind:DefaultProductKindSpec"],
        "system_setting_keys": [
            "shuup.core.setting_keys",
        ],
    }

    def ready(self):
        from django.conf import settings

        if not getattr(settings, "PARLER_DEFAULT_LANGUAGE_CODE", None):
            raise MissingSettingException("PARLER_DEFAULT_LANGUAGE_CODE must be set.")
        if not getattr(settings, "PARLER_LANGUAGES", None):
            raise MissingSettingException("PARLER_LANGUAGES must be set.")

        # set money precision provider function
        from .models import get_currency_precision

        money.set_precision_provider(get_currency_precision)

        if django.conf.settings.SHUUP_ERROR_PAGE_HANDLERS_SPEC:
            from .error_handling import install_error_handlers

            install_error_handlers()

        # connect signals
        import shuup.core.signal_handlers  # noqa: F401


default_app_config = "shuup.core.ShuupCoreAppConfig"

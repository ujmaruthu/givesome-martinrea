# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.discounts"
    provides = {
        "admin_module": [
            "shuup.discounts.admin.modules.DiscountModule",
            "shuup.discounts.admin.modules.DiscountArchiveModule",
            "shuup.discounts.admin.modules.HappyHourModule",
        ],
        "admin_object_selector": [
            "shuup.discounts.admin.object_selector.DiscountAdminObjectSelector",
        ],
        "discount_module": ["shuup.discounts.modules:ProductDiscountModule"],
        "xtheme_plugin": ["shuup.discounts.plugins:DiscountedProductsPlugin"],
    }

    def ready(self):
        import shuup.discounts.signal_handlers  # noqa: F401

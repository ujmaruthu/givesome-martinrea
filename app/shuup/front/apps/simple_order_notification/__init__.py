# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.apps import AppConfig


class SimpleOrderNotificationAppConfig(AppConfig):
    name = "shuup.front.apps.simple_order_notification"
    verbose_name = "Shuup Frontend - Simple Order Notification"
    label = "shuup_front.simple_order_notification"

    provides = {
        "admin_module": [
            "shuup.front.apps.simple_order_notification.admin_module:SimpleOrderNotificationModule",
        ]
    }


default_app_config = "shuup.front.apps.simple_order_notification.SimpleOrderNotificationAppConfig"

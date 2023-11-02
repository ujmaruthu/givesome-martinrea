# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = "shuup.front.apps.auth"
    verbose_name = "Shuup Frontend - User Authentication"
    label = "shuup_front.auth"

    provides = {
        "front_urls": ["shuup.front.apps.auth.urls:urlpatterns"],
    }


default_app_config = "shuup.front.apps.auth.AuthAppConfig"

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.core.utils.static import get_shuup_static_url
from shuup.xtheme.resources import add_resource


def add_givesome_resources(context, content):
    request = context.get("request")
    if not request:
        return

    match = request.resolver_match
    if not match:
        return

    if match.app_name == "shuup_admin":
        add_resource(context, "body_end", get_shuup_static_url("givesome/admin_scripts.js", "givesome-marketplace"))

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.utils.translation import activate
from shuup import configuration as shuup_config
from shuup.admin.utils.permissions import get_permissions_from_group
from shuup.core.models import ConfigurationItem


class Command(BaseCommand):
    def handle(self, *args, **options):
        activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)
        config = {"group_permissions": {}, "api_permissions": []}

        # Fetch prmissions based on known permission groups
        group_names = [
            settings.STAFF_PERMISSION_GROUP_NAME,
            "Staff Menu Edit Permissions",
            settings.VENDORS_PERMISSION_GROUP_NAME,
            "Vendor Menu Edit Permissions",
            "Charity",
            "Brand",
        ]

        for group_name in group_names:
            group = Group.objects.filter(name=group_name).first()
            if not group:
                continue
            config["group_permissions"][group_name] = list(sorted(get_permissions_from_group(group)))

        # Fetch customized menus based for staff and vendors
        config["admin_menu_staff"] = shuup_config.get(None, "admin_menu_staff", {})
        config["admin_menu_supplier"] = shuup_config.get(None, "admin_menu_supplier", {})

        # Fetch API permissions
        for configuration_item in ConfigurationItem.objects.filter(key__startswith="api_permission_"):
            config["api_permissions"].append({"key": configuration_item.key, "value": configuration_item.value})

        with open("config.json", "w") as f:
            json.dump(config, f, indent=4, sort_keys=True)

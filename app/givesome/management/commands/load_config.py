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
from shuup.admin.utils.permissions import set_permissions_for_group


class Command(BaseCommand):
    def handle(self, *args, **options):
        activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)
        with open("config.json") as f:
            config = json.load(f)

        group_permissions = config.get("group_permissions")
        if group_permissions:
            # Set permissions based on known permission groups
            group_names = [
                settings.STAFF_PERMISSION_GROUP_NAME,
                "Staff Menu Edit Permissions",
                settings.VENDORS_PERMISSION_GROUP_NAME,
                "Vendor Menu Edit Permissions",
                "Charity",
                "Brand",
            ]

            for group_name in group_names:
                if group_name not in group_permissions:
                    continue

                group = Group.objects.filter(name=group_name).first()
                if not group:
                    continue

                set_permissions_for_group(group, group_permissions[group_name])

        # Set customized menus based for staff and vendors
        shuup_config.set(None, "admin_menu_staff", config.get("admin_menu_staff", {}))
        shuup_config.set(None, "admin_menu_supplier", config.get("admin_menu_supplier", {}))

        # Fetch API permissions
        for permission_dict in config.get("api_permissions", []):
            shuup_config.set(None, permission_dict["key"], permission_dict["value"])

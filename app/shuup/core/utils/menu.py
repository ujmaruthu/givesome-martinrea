# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.


class MainMenuUpdater(object):

    """
    To update items add for example
    updates = {
        PRODUCTS_MENU_CATEGORY: [{"identifier": "subscriptions", "title": _("Subscriptions")}],
        ORDERS_MENU_CATEGORY: [{"identifier": "subscriptions", "title": _("Subscriptions")}]
    }
    """

    updates = {}

    def __init__(self, menu):
        self.menu = menu

    def update(self):
        """
        Update the `shuup.admin.menu.MAIN_MENU`
        :return:
        """
        for item in self.menu:
            for child in self.updates.get(item["identifier"], []):
                try:
                    if child not in item["entries"]:
                        item["entries"].append(child)
                except KeyError:
                    item["entries"] = [child]
        return self.menu

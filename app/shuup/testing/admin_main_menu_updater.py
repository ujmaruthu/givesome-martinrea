# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from shuup.admin.menu import PRODUCTS_MENU_CATEGORY
from shuup.core.utils.menu import MainMenuUpdater


class TestAdminMainMenuUpdater(MainMenuUpdater):
    updates = {
        PRODUCTS_MENU_CATEGORY: [
            {"identifier": "test_0", "title": "Test 0"},
            {"identifier": "test_1", "title": "Test 1"},
        ],
    }

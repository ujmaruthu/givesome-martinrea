# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class OrderReferenceNumberMethod(Enum):
    UNIQUE = "unique"
    RUNNING = "running"
    SHOP_RUNNING = "shop_running"

    class Labels:
        UNIQUE = _("unique")
        RUNNING = _("running")
        SHOP_RUNNING = _("shop running")

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class StockAdjustmentType(Enum):
    INVENTORY = 1
    RESTOCK = 2
    RESTOCK_LOGICAL = 3

    class Labels:
        INVENTORY = _("inventory")
        RESTOCK = _("restock")
        RESTOCK_LOGICAL = _("restock logical")

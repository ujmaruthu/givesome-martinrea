# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import decimal

from shuup.core.fields import MONEY_FIELD_DECIMAL_PLACES


def ensure_decimal_places(value):
    return value.quantize(decimal.Decimal(".1") ** MONEY_FIELD_DECIMAL_PLACES)

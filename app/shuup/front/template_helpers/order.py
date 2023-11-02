# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from typing import Iterable

from shuup.core.models import OrderLine
from shuup.front.utils.order_source import LineProperty, get_line_properties


def get_properties_from_line(line: OrderLine) -> Iterable[LineProperty]:
    return list(get_line_properties(line))

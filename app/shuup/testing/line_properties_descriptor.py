# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.front.utils.order_source import BaseLinePropertiesDescriptor, LineProperty


class TestLinePropertiesDescriptor(BaseLinePropertiesDescriptor):
    @classmethod
    def get_line_properties(cls, line, **kwargs):
        yield LineProperty("Type", str(line.type))

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.


class OrderInformation(object):
    order = 1
    title = "default"

    def __init__(self, order, **kwargs):
        self.order = order

    def provides_info(self):
        """
        Override to add business logic if the order should show this information row.
        """
        return self.information is not None

    @property
    def information(self):
        """
        Override this property to return wanted information about the order.
        """
        return None

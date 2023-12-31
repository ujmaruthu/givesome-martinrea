# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.core.models import Order
from shuup.notify.base import Action, Binding, ConstantUse
from shuup.notify.typology import Model, Text


class AddOrderLogEntry(Action):
    identifier = "add_order_log_entry"
    order = Binding("Order", Model("shuup.Order"), constant_use=ConstantUse.VARIABLE_ONLY)
    message = Binding("Message", Text, constant_use=ConstantUse.VARIABLE_OR_CONSTANT)
    message_identifier = Binding("Message Identifier", Text, constant_use=ConstantUse.VARIABLE_OR_CONSTANT)

    def execute(self, context):
        order = self.get_value(context, "order")
        if not order:  # pragma: no cover
            return
        message = self.get_value(context, "message")
        message_identifier = self.get_value(context, "message_identifier") or None
        assert isinstance(order, Order)
        order.add_log_entry(message=message, identifier=message_identifier)

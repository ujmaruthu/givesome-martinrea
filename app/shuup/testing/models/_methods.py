# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from shuup.core.models import CustomCarrier, CustomPaymentProcessor, PaymentStatus


class CarrierWithCheckoutPhase(CustomCarrier):
    pass


class PaymentWithCheckoutPhase(CustomPaymentProcessor):
    def process_payment_return_request(self, service, order, request):
        if order.payment_status == PaymentStatus.NOT_PAID and order.payment_data.get("input_value"):
            order.payment_status = PaymentStatus.DEFERRED
            order.add_log_entry("Info! Customer promised to pay his bills.")
            order.save(update_fields=("payment_status",))

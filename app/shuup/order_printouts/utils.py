# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.


class PrintoutDeliveryExtraInformation(object):
    order = 1

    def __init__(self, order, shipment, **kwargs):
        self.order = order
        self.shipment = shipment

    def provides_extra_fields(self):
        """
        Override to add business logic if this module has any extra fields to add
        to the delivery printout.
        """
        return self.extra_fields is not None

    @property
    def extra_fields(self):
        """
        Override this property to return wanted information about the order.
        This property should return a dictionary of field names and values
        which will be rendered to the order delivery printout.
        """
        return {}

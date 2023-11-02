# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2017, Anders Innovations. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.exceptions import ObjectDoesNotExist

from shuup.core.models._units import PiecesSalesUnit, UnitInterface


class LineWithUnit(object):
    @property
    def unit(self):
        """
        Unit of this line.

        :rtype: UnitInterface
        """
        # TODO: Store the sales unit and display unit to the line
        if not self.product or not self.product.sales_unit or not self.shop:
            return UnitInterface(PiecesSalesUnit())
        try:
            shop_product = self.product.get_shop_instance(self.shop)
        except ObjectDoesNotExist:
            return UnitInterface(self.product.sales_unit)
        return shop_product.unit

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.utils.excs import Problem


class ImmutabilityError(ValueError):
    pass


class NoShippingAddressException(Exception):
    pass


class NoProductsToShipException(Exception):
    pass


class NoPaymentToCreateException(Exception):
    pass


class NoRefundToCreateException(Exception):
    pass


class RefundArbitraryRefundsNotAllowedException(Exception):
    pass


class RefundExceedsAmountException(Exception):
    pass


class RefundExceedsQuantityException(Exception):
    pass


class InvalidRefundAmountException(Exception):
    pass


class MissingSettingException(Exception):
    pass


class ProductNotOrderableProblem(Problem):
    pass


class ProductNotVisibleProblem(Problem):
    pass


class InvalidOrderStatusError(Problem):
    pass


class ImpossibleProductModeException(ValueError):
    def __init__(self, message, code=None):
        super(ImpossibleProductModeException, self).__init__(message)
        self.code = code


class SupplierHasNoSupplierModules(Exception):
    pass


class UnavailableError(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code

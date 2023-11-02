# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

import datetime
from django.conf import settings

from shuup.core.constants import DEFAULT_REFERENCE_NUMBER_LENGTH
from shuup.core.setting_keys import (
    SHUUP_REFERENCE_NUMBER_LENGTH,
    SHUUP_REFERENCE_NUMBER_METHOD,
    SHUUP_REFERENCE_NUMBER_PREFIX,
)
from shuup.utils.django_compat import force_text
from shuup.utils.importing import load

from ._counters import Counter, CounterType


def calc_reference_number_checksum(rn):
    muls = (7, 3, 1)
    s = 0
    for i, ch in enumerate(rn[::-1]):
        s += muls[i % 3] * int(ch)
    s = 10 - (s % 10)
    return force_text(s)[-1]


def get_unique_reference_number(shop, id):
    from shuup import configuration

    now = datetime.datetime.now()

    ref_length = configuration.get(shop, SHUUP_REFERENCE_NUMBER_LENGTH, DEFAULT_REFERENCE_NUMBER_LENGTH)
    dt = ("%06s%07d%04d" % (now.strftime("%y%m%d"), now.microsecond, id % 1000)).rjust(ref_length, "0")
    return dt + calc_reference_number_checksum(dt)


def get_unique_reference_number_for_order(order):
    return get_unique_reference_number(order.shop, order.pk)


def get_running_reference_number(order):
    from shuup import configuration

    value = Counter.get_and_increment(CounterType.ORDER_REFERENCE)
    prefix = "%s" % configuration.get(order.shop, SHUUP_REFERENCE_NUMBER_PREFIX)
    ref_length = configuration.get(order.shop, SHUUP_REFERENCE_NUMBER_LENGTH, DEFAULT_REFERENCE_NUMBER_LENGTH)

    padded_value = force_text(value).rjust(ref_length - len(prefix), "0")
    reference_no = "%s%s" % (prefix, padded_value)
    return reference_no + calc_reference_number_checksum(reference_no)


def get_shop_running_reference_number(order):
    from shuup import configuration

    value = Counter.get_and_increment(CounterType.ORDER_REFERENCE)
    prefix = "%06d" % order.shop.pk
    ref_length = configuration.get(order.shop, SHUUP_REFERENCE_NUMBER_LENGTH, DEFAULT_REFERENCE_NUMBER_LENGTH)
    padded_value = force_text(value).rjust(ref_length - len(prefix), "0")
    reference_no = "%s%s" % (prefix, padded_value)
    return reference_no + calc_reference_number_checksum(reference_no)


def get_reference_number(order):
    from shuup import configuration
    from shuup.admin.modules.settings.enums import OrderReferenceNumberMethod

    if order.reference_number:
        raise ValueError("Error! Order passed to function `get_reference_number()` already has a reference number.")
    reference_number_method = configuration.get(
        order.shop, SHUUP_REFERENCE_NUMBER_METHOD, DEFAULT_REFERENCE_NUMBER_LENGTH
    )
    if reference_number_method == OrderReferenceNumberMethod.UNIQUE.value:
        return get_unique_reference_number_for_order(order)
    elif reference_number_method == OrderReferenceNumberMethod.RUNNING.value:
        return get_running_reference_number(order)
    elif reference_number_method == OrderReferenceNumberMethod.SHOP_RUNNING.value:
        return get_shop_running_reference_number(order)
    elif callable(reference_number_method):
        return reference_number_method(order)
    else:
        getter = load(reference_number_method, "Reference number generator")
        return getter(order)


def get_order_identifier(order):
    if order.identifier:
        raise ValueError("Error! Order passed to function `get_order_identifier()` already has an identifier.")
    order_identifier_method = settings.SHUUP_ORDER_IDENTIFIER_METHOD
    if order_identifier_method == "id":
        return force_text(order.id)
    elif callable(order_identifier_method):
        return order_identifier_method(order)
    else:
        getter = load(order_identifier_method, "Order identifier generator")
        return getter(order)

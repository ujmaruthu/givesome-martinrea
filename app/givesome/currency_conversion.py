# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from decimal import Decimal
from typing import Union

from django.contrib.auth.models import User
from shuup.core import cache
from shuup_multicurrencies_display.models import Rate


def givesome_exchange_currency(user: User, value: Union[int, Decimal, str]) -> Decimal:
    """Calculate `value` based on the user's preferred currency and today's exchange rates, if possible.
    Note: the API calculates with a USD base, but the shop base currency is CAD. So make the necessary conversions.
    """

    value = Decimal(value)
    currencies = cache.get("currencies")
    preferred_currency = getattr(user, "preferred_currency", None)
    if preferred_currency is None:
        # No need to calculate anything
        return value

    if not currencies:
        try:
            CAD = Rate.objects.filter(base_currency__currency__identifier="USD", currency__identifier="CAD").first()
            rate = Rate.objects.filter(
                base_currency__currency__identifier="USD", currency=preferred_currency.currency
            ).first()
        except Exception:
            # The build process attempts to execute these queries, which is problematic if the tables haven't been
            # migrated yet, because migration expects a successful build before it will start migrating.
            return value
        currencies = {"cad_currency": CAD, "rates": {preferred_currency.currency: rate}}
        cache.set("currencies", currencies)
    else:
        CAD = currencies["cad_currency"]
        rate = currencies["rates"].get(preferred_currency.currency)
        if not rate:
            rate = currencies["rates"][preferred_currency.currency] = Rate.objects.filter(
                base_currency__currency__identifier="USD", currency=preferred_currency.currency
            ).first()

    if rate and preferred_currency and preferred_currency.currency:
        usd_base = 1 / CAD.value
        new_value = round(usd_base * rate.value * value, 2)
        return new_value
    return value


def convert_to_shop_currency(user, value: Decimal) -> Decimal:
    """If the user is in non-CAD currency, calculate the CAD equivalent."""
    if (
        hasattr(user, "preferred_currency")
        and user.preferred_currency.currency
        and user.preferred_currency.currency.identifier != "CAD"
    ):
        user_rate = Rate.objects.filter(
            base_currency__currency__identifier="USD", currency=user.preferred_currency.currency
        ).first()
        cad_rate = Rate.objects.filter(base_currency__currency__identifier="USD", currency__identifier="CAD").first()
        usd_base = 1 / user_rate.value
        return round(usd_base * cad_rate.value * value, 2)
    return value


def get_preferred_currency(user) -> str:
    if hasattr(user, "preferred_currency") and user.preferred_currency.currency:
        return user.preferred_currency.currency.identifier
    return "CAD"

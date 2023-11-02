# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.management.base import BaseCommand
from shuup import configuration
from shuup.core import cache
from shuup.core.models import Shop
from shuup_multicurrencies_display.backends import REGISTERED_BACKENDS, FrequencyBasedRatesUpdater
from shuup_multicurrencies_display.configuration import EXCHANGE_RATES_SOURCE, EXCHANGE_RATES_UPDATE_FREQUENCY
from shuup_multicurrencies_display.models import Rate


class Command(BaseCommand):
    help = "Populate currency exchange rates based on frequency"

    def handle(self, *args, **options):
        shop = Shop.objects.first()
        source_name = configuration.get(shop, EXCHANGE_RATES_SOURCE)
        update_frequency = configuration.get(shop, EXCHANGE_RATES_UPDATE_FREQUENCY)
        if source_name and update_frequency:
            # Note: only USD is accepted by Open Exchange Rates as a base currency (on the free tier)
            api = REGISTERED_BACKENDS[configuration.get(shop, EXCHANGE_RATES_SOURCE)]("USD")
            updater = FrequencyBasedRatesUpdater(api=api, frequency=update_frequency)
            updater.update_rates()

        # Clear the cache of yesterday's rates
        currencies = cache.get("currencies")
        if currencies:
            currencies = {
                "cad_currency": Rate.objects.filter(
                    base_currency__currency__identifier="USD", currency__identifier="CAD"
                ).first(),
                "rates": {},
            }
            cache.set("currencies", currencies)

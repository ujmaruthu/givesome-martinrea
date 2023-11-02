# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from datetime import timedelta

import pytest
from django.utils import timezone

from givesome.enums import GivecardDonateRestrictionType as GDRT
from givesome.models import Givecard, GivecardBatch
from givesome_tests.factories import givecard_batch_factory, givecard_campaign_factory
from givesome_tests.utils import create_layers_of_offices


@pytest.mark.django_db
def test_order_givecards_for_checkout_based_on_restrictions(vendor_user_brand):
    """These are explained in more detail in `GivecardQuerySet.order_for_checkout()` docstring"""
    supplier = vendor_user_brand.vendor
    office = vendor_user_brand.office
    office2 = vendor_user_brand.office2
    office3 = vendor_user_brand.office3
    create_layers_of_offices(vendor_user_brand)

    campaign = givecard_campaign_factory()
    common_values = [
        1,  # amount
        1,  # value
        campaign,  # campaign
    ]

    # Most restrictive Givecards, restricted to a Office
    batch1_1 = givecard_batch_factory(*common_values, supplier, office, restriction_type=GDRT.OFFICE)
    batch1_2 = givecard_batch_factory(*common_values, supplier, office2, restriction_type=GDRT.OFFICE)
    batch1_3 = givecard_batch_factory(*common_values, supplier, office3, restriction_type=GDRT.OFFICE)

    # "Medium" restricted Givecards, restricted to a Supplier
    batch2_1 = givecard_batch_factory(*common_values, supplier, None, restriction_type=GDRT.OFFICE)
    batch2_2 = givecard_batch_factory(*common_values, supplier, office, restriction_type=GDRT.SUPPLIER)
    batch2_3 = givecard_batch_factory(*common_values, supplier, None, restriction_type=GDRT.SUPPLIER)
    group_2 = [batch2_1, batch2_2, batch2_3]

    # Least restricted Givecards, not restricted at all
    batch3_1 = givecard_batch_factory(*common_values, None, None, restriction_type=GDRT.OFFICE)
    batch3_2 = givecard_batch_factory(*common_values, None, None, restriction_type=GDRT.SUPPLIER)
    batch3_3 = givecard_batch_factory(*common_values, supplier, office, restriction_type=GDRT.DISABLED)
    batch3_4 = givecard_batch_factory(*common_values, supplier, None, restriction_type=GDRT.DISABLED)
    batch3_5 = givecard_batch_factory(*common_values, None, None, restriction_type=GDRT.DISABLED)
    group_3 = [batch3_1, batch3_2, batch3_3, batch3_4, batch3_5]

    [batch.generate_givecards() for batch in GivecardBatch.objects.all()]
    assert Givecard.objects.all().count() == 11

    givecards = list(Givecard.objects.all().order_for_checkout())

    # 1. Office Restriction
    assert givecards[0].batch == batch1_3  # Most restrictive office, sub-sub-office
    assert givecards[1].batch == batch1_2  # sub-office
    assert givecards[2].batch == batch1_1  # Office doesn't have any parents

    # 2. Supplier Restriction
    assert givecards[3].batch in group_2  # Order in this group is not important
    assert givecards[4].batch in group_2
    assert givecards[5].batch in group_2

    # 3. No Restriction
    assert givecards[6].batch in group_3  # Order in this group is not important
    assert givecards[7].batch in group_3
    assert givecards[8].batch in group_3
    assert givecards[9].batch in group_3
    assert givecards[10].batch in group_3


@pytest.mark.django_db
def test_order_givecards_for_checkout_based_on_expiry(vendor_user_brand):
    supplier = vendor_user_brand.vendor
    campaign = givecard_campaign_factory()

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    common_values = [
        1,  # amount
        1,  # value
        campaign,  # campaign
    ]

    batch1 = givecard_batch_factory(*common_values, supplier, expiration_date=yesterday)
    batch2 = givecard_batch_factory(*common_values, supplier, expiration_date=today)
    batch3 = givecard_batch_factory(*common_values, supplier, expiration_date=tomorrow)
    batch4 = givecard_batch_factory(*common_values, supplier, expiration_date=None)

    batch5 = givecard_batch_factory(*common_values, expiration_date=today)
    batch6 = givecard_batch_factory(*common_values, expiration_date=None)

    [batch.generate_givecards() for batch in GivecardBatch.objects.all()]
    assert Givecard.objects.all().count() == 6

    givecards = list(Givecard.objects.all().order_for_checkout())

    # Givecards expiring first should be returned first
    assert givecards[0].batch == batch1
    assert givecards[1].batch == batch2
    assert givecards[2].batch == batch3
    assert givecards[3].batch == batch4

    # Givecards with less strict restriction always come after, regardless of expiration
    assert givecards[4].batch == batch5
    assert givecards[5].batch == batch6

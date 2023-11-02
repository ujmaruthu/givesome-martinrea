# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

import pytest
from django.utils import timezone

from givesome.enums import GivecardDonateRestrictionType
from givesome.models import Givecard
from givesome_tests.factories import givecard_batch_factory, givecard_campaign_factory, givecard_factory
from givesome_tests.utils import create_layers_of_offices


@pytest.mark.django_db
def test_givecard_usable_filter():
    # Valid givecard
    givecard_factory(campaign=givecard_campaign_factory())
    assert Givecard.objects.usable().count() == 1

    # Expired givecard
    givecard_factory(batch=givecard_batch_factory(expiration_date=timezone.localdate()))
    assert Givecard.objects.usable().count() == 1

    # No campaign set
    givecard_factory(batch=givecard_batch_factory(campaign=None))
    assert Givecard.objects.usable().count() == 1

    # No balance left
    givecard_factory(balance=0)
    assert Givecard.objects.usable().count() == 1


@pytest.mark.django_db
def test_givecard_is_checkout_possible_with_supplier_office_and_no_restrictions(vendor_user_brand, vendor_user_brand_2):
    vendor = vendor_user_brand.vendor
    vendor2 = vendor_user_brand_2.vendor
    office = vendor_user_brand.office
    office2 = vendor_user_brand.office2

    # Test office restriction
    campaign = givecard_campaign_factory(supplier=vendor)
    batch = givecard_batch_factory(
        campaign=campaign,
        supplier=vendor,
        office=office,
        restriction_type=GivecardDonateRestrictionType.OFFICE,
    ).generate_givecards()
    givecards = batch.givecards

    # No promoters so only unrestricted Givecards are allowed. This batch is restricted so checkout is not possible.
    assert not givecards.is_checkout_possible()
    # Promoter matches restriction perfectly
    assert givecards.is_checkout_possible(promoter=office)
    # Promoter is wrong office
    assert not givecards.is_checkout_possible(promoter=office2)
    # Batch has `Office` restriction, and promoter is vendor
    assert not givecards.is_checkout_possible(promoter=vendor)

    # Test Supplier restriction
    batch.restriction_type = GivecardDonateRestrictionType.SUPPLIER
    batch.save()

    # No promoter given, but batch has a restriction
    assert not givecards.is_checkout_possible()
    # Batch is restricted to supplier, but promoter is wrong supplier
    assert not givecards.is_checkout_possible(promoter=vendor2)
    # Batch is restricted to supplier, promoter is the same supplier, all ok
    assert givecards.is_checkout_possible(promoter=vendor)
    # Batch is restricted to supplier, which are under the supplier
    assert givecards.is_checkout_possible(promoter=office)
    assert givecards.is_checkout_possible(promoter=office2)

    # Test No restriction
    batch.restriction_type = GivecardDonateRestrictionType.DISABLED
    batch.save()

    # Non-restricted Givecards are valid to use anywhere
    assert givecards.is_checkout_possible()
    assert givecards.is_checkout_possible(promoter=vendor)
    assert givecards.is_checkout_possible(promoter=vendor2)
    assert givecards.is_checkout_possible(promoter=office)
    assert givecards.is_checkout_possible(promoter=office2)


@pytest.mark.django_db
def test_givecard_is_checkout_possible_layers_of_offices(vendor_user_brand, vendor_user_brand_2):
    vendor = vendor_user_brand.vendor
    office = vendor_user_brand.office
    office2 = vendor_user_brand.office2
    office3 = vendor_user_brand.office3
    create_layers_of_offices(vendor_user_brand)

    # Test office restriction
    campaign = givecard_campaign_factory(supplier=vendor)
    batch = givecard_batch_factory(
        campaign=campaign,
        supplier=vendor,
        restriction_type=GivecardDonateRestrictionType.OFFICE,
    ).generate_givecards()

    # No office set, Givecards can be donated in any Office
    assert batch.givecards.is_checkout_possible(office)
    assert batch.givecards.is_checkout_possible(office2)
    assert batch.givecards.is_checkout_possible(office3)

    # Restricted to level 0 office, it and all child offices are valid
    batch.office = office
    batch.save()
    assert batch.givecards.is_checkout_possible(office)
    assert batch.givecards.is_checkout_possible(office2)
    assert batch.givecards.is_checkout_possible(office3)

    # Restricted to level 1 office, Child offices are valid, but higher level is not
    batch.office = office2
    batch.save()
    assert not batch.givecards.is_checkout_possible(office)
    assert batch.givecards.is_checkout_possible(office2)
    assert batch.givecards.is_checkout_possible(office3)

    # Restricted to level 3 office, only it is valid as it has no children
    batch.office = office3
    batch.save()
    assert not batch.givecards.is_checkout_possible(office)
    assert not batch.givecards.is_checkout_possible(office2)
    assert batch.givecards.is_checkout_possible(office3)

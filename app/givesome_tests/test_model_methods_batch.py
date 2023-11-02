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
from django.core.exceptions import ValidationError
from django.utils import timezone

from givesome.enums import GivecardBatchExpiryType
from givesome.models import Givecard, GivecardBatch
from givesome.models.givecard_batch import NullifiedGivecardBatch
from givesome_tests.factories import givecard_batch_factory, givecard_campaign_factory


@pytest.mark.django_db
def test_batch_generate_givecards():
    campaign = givecard_campaign_factory()

    # Generate Multicards
    batch_multi = givecard_batch_factory(campaign=campaign, amount=100, value=2, code="AAAAAA")
    batch_multi.generate_givecards()
    assert Givecard.objects.all().count() == 100

    # Generate Unique Givecards
    batch_unique = givecard_batch_factory(campaign=campaign, amount=100, value=5)
    batch_unique.generate_givecards()
    assert Givecard.objects.all().count() == 200
    assert Givecard.objects.filter(code__isnull=True).count() == 100

    assert batch_multi.givecards.first().balance == 2
    assert batch_unique.givecards.first().balance == 5

    # Batch can be generated only once
    with pytest.raises(ValidationError):
        batch_unique.generate_givecards()


@pytest.mark.django_db
def test_batch_valid_code_format():
    # Valid
    givecard_batch_factory(code="AAAAAA").clean_code()
    givecard_batch_factory(code="AAAAA1").clean_code()
    givecard_batch_factory(code="123456").clean_code()

    # Invalid
    with pytest.raises(ValidationError):
        givecard_batch_factory(code="AAAAA").clean_code()
    with pytest.raises(ValidationError):
        givecard_batch_factory(code="AAAAAAA").clean_code()
    with pytest.raises(ValidationError):
        givecard_batch_factory(code="AAAAAa").clean_code()


@pytest.mark.django_db
def test_batch_clean_dates():
    """Test GivecardBatch cannot be given invalid dates"""

    def set_and_validate_dates(batch, d1, d2, d3):
        batch.redemption_start_date = d1
        batch.redemption_end_date = d2
        batch.expiration_date = d3
        batch.clean()

    batch = givecard_batch_factory(code="AAAAAA")
    now = timezone.localdate()
    day = timedelta(days=1)

    # Valid dates
    set_and_validate_dates(batch, now, now, now)
    set_and_validate_dates(batch, now - day, now, now + day)

    # Invalid dates
    with pytest.raises(ValidationError):
        set_and_validate_dates(batch, now + day, now, None)
    with pytest.raises(ValidationError):
        set_and_validate_dates(batch, now + day, None, now)
    with pytest.raises(ValidationError):
        set_and_validate_dates(batch, None, now + day, now)


@pytest.mark.django_db
def test_batch_clean_supplier_office(vendor_user_brand, vendor_user_brand_2):
    office = vendor_user_brand.office
    office2 = vendor_user_brand_2.office
    batch = givecard_batch_factory()

    # No Supplier or Office set
    batch.clean()

    # No supplier, with office is invalid
    with pytest.raises(ValidationError):
        batch.office = office
        batch.clean()

    # Supplier set and Office belonging to Supplier is valid
    batch.supplier = office.supplier
    batch.clean()

    # Office and Supplier mismatch
    with pytest.raises(ValidationError):
        batch.supplier = office2.supplier
        batch.clean()


@pytest.mark.django_db
def test_batch_total_balance():
    batch = givecard_batch_factory(amount=50, value=10)
    assert batch.total_balance == 0
    batch.generate_givecards()
    assert batch.total_balance == 500


@pytest.mark.django_db
def test_batch_str():
    batch = givecard_batch_factory(amount=5, value=10)
    assert str(batch) == "Givecard Batch (1)"

    batch.generate_givecards()
    assert str(batch) == "Givecard Batch (1) [5 x $10]"

    batch = givecard_batch_factory(code="AAAAAA", amount=5, value=10)
    assert str(batch) == "Multicard Batch (AAAAAA)"

    batch.generate_givecards()
    assert str(batch) == "Multicard Batch (AAAAAA) [5 x $10]"


@pytest.mark.django_db
def test_batch_original_balance():
    batch = givecard_batch_factory(amount=10, value=10)
    assert batch.original_balance == 0

    batch.generate_givecards()
    assert batch.original_balance == 100


@pytest.mark.django_db
def test_batch_nullify(vendor_user_brand):
    batch = givecard_batch_factory(
        amount=10,
        value=10,
        expiry_type=GivecardBatchExpiryType.AUTOMATIC,
        expiration_date=timezone.localdate() + timedelta(days=1),
    )
    batch.generate_givecards()

    with pytest.raises(ValidationError):
        batch.nullify(nullifier=vendor_user_brand.user.contact)

    batch.expiry_type = GivecardBatchExpiryType.MANUAL
    batch.save()
    with pytest.raises(ValidationError):
        batch.nullify(nullifier=vendor_user_brand.user.contact)

    batch.expiration_date = None
    batch.save()
    batch.nullify(nullifier=vendor_user_brand.user.contact)

    assert batch.total_balance == 0
    nullified_batch = NullifiedGivecardBatch.objects.get(batch=batch)
    assert nullified_batch.amount == 100


####################
# Queryset Methods #
####################


@pytest.mark.django_db
def test_batch_expired_filter():
    now = timezone.localdate()
    day = timedelta(days=1)

    givecard_batch_factory()
    assert GivecardBatch.objects.expired().count() == 0

    givecard_batch_factory(expiration_date=now - day)
    assert GivecardBatch.objects.expired().count() == 1

    givecard_batch_factory(expiration_date=now + day)
    assert GivecardBatch.objects.expired().count() == 1

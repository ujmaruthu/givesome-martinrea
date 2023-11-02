# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from givesome_tests.factories import givecard_batch_factory, givecard_campaign_factory, givecard_factory


@pytest.mark.django_db
def test_givecard_valid_code_format():
    # Valid
    givecard_factory(code="AAAAAA").clean_code()
    givecard_factory(code="AAAAA1").clean_code()
    givecard_factory(code="123456").clean_code()

    # Invalid
    with pytest.raises(ValidationError):
        givecard_factory(code="AAAAA").clean_code()
    with pytest.raises(ValidationError):
        givecard_factory(code="AAAAAAA").clean_code()
    with pytest.raises(ValidationError):
        givecard_factory(code="AAAAAa").clean_code()


@pytest.mark.django_db
def test_givecard_duplicate_code_with_givecard_and_givecard():
    with pytest.raises(ValidationError):
        givecard_factory(code="AAAAAA")
        givecard_factory(code="AAAAAA").clean_code()


@pytest.mark.django_db
def test_givecard_duplicate_code_with_multicard_and_multicard():
    with pytest.raises(ValidationError):
        givecard_batch_factory(code="AAAAAA")
        givecard_batch_factory(code="AAAAAA").generate_givecards()


@pytest.mark.django_db
def test_givecard_duplicate_code_with_givecard_and_multicard():
    with pytest.raises(ValidationError):
        givecard_factory(code="AAAAAA")
        givecard_batch_factory(code="AAAAAA").generate_givecards()


@pytest.mark.django_db
def test_givecard_duplicate_code_with_multicard_and_givecard():
    with pytest.raises(ValidationError):
        givecard_batch_factory(code="AAAAAA")
        givecard_factory(code="AAAAAA").clean()


@pytest.mark.django_db
def test_givecard_get_code():
    campaign = givecard_campaign_factory()
    # Unique Givecard PINs
    batch = givecard_batch_factory(campaign=campaign, code=None).generate_givecards()
    assert batch.givecards.first().get_code() is not None

    # Multicards
    batch = givecard_batch_factory(campaign=campaign, code="ABCABC").generate_givecards()
    assert batch.givecards.first().get_code() is not None

    # Invalid batch
    batch.code = None
    batch.save()
    with pytest.raises(ValueError):
        batch.givecards.first().get_code()


@pytest.mark.django_db
def test_givecard_get_data_for_wallet_expiring(vendor_user_brand):
    campaign = givecard_campaign_factory()
    batch = givecard_batch_factory(
        expiration_date=timezone.localdate(),
        supplier=vendor_user_brand.vendor,
        office=vendor_user_brand.office,
        campaign=campaign,
    )
    givecard = givecard_factory(batch=batch, code="AAAAAA", balance=10)
    data = givecard.get_data_for_wallet()

    assert "exp_date" in data
    assert data["code"] == "AAAAAA"
    assert data["balance"] == 10
    assert data["supplier"] == 1
    assert data["office"] == 1
    assert data["is_expiring_soon"] is True
    assert "exp_date" in data


@pytest.mark.django_db
def test_givecard_get_data_for_wallet_not_expiring():
    campaign = givecard_campaign_factory()
    batch = givecard_batch_factory(campaign=campaign)
    givecard = givecard_factory(batch=batch)
    data = givecard.get_data_for_wallet()

    assert data["is_expiring_soon"] is False
    assert "exp_date" not in data

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
from django.core.management import call_command
from django.utils import timezone
from shuup.core.defaults.order_statuses import create_default_order_statuses

from givesome.enums import GivecardBatchExpiryType
from givesome_tests.factories import (
    create_givesome_purse_allocation,
    get_default_purse,
    givecard_batch_factory,
    givecard_campaign_factory,
)
from givesome_tests.test_givecard_expiry_auto import change_project_goal


@pytest.mark.django_db
def test_funds_are_moved_to_givesome_purse_batch_has_no_supplier():
    purse = get_default_purse()
    batch = givecard_batch_factory(
        amount=100,
        value=1,
        campaign=givecard_campaign_factory(),
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
        expiry_type=GivecardBatchExpiryType.MANUAL,
    ).generate_givecards()

    call_command("handle_expired_givecards")
    purse.refresh_from_db()

    assert batch.total_balance == 0
    assert purse.balance == 100
    assert batch.givecards.first().automatically_donated == 1  # Record amount that was moved


def _create_and_handle_expired_batch(supplier):
    common_values = dict(
        amount=1,
        value=100,
        campaign=givecard_campaign_factory(),
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
        supplier=supplier,
    )
    batch = givecard_batch_factory(
        **common_values,
        expiry_type=GivecardBatchExpiryType.MANUAL,
    ).generate_givecards()

    batch2 = givecard_batch_factory(
        **common_values,
        expiry_type=GivecardBatchExpiryType.AUTOMATIC,
    ).generate_givecards()

    call_command("handle_expired_givecards")
    assert batch.total_balance == 0
    assert batch.givecards.first().automatically_donated == 100  # Record amount that was moved
    assert batch2.total_balance == 0
    assert batch2.givecards.first().automatically_donated == 100  # Record amount that was moved


@pytest.mark.django_db
def test_funds_are_moved_to_brand_purse_allowed(vendor_user_brand):
    givesome_purse = get_default_purse(supplier=None)  # By default allow_purse is `True`
    brand_purse = get_default_purse(supplier=vendor_user_brand.vendor)
    _create_and_handle_expired_batch(supplier=vendor_user_brand.vendor)

    givesome_purse.refresh_from_db()
    brand_purse.refresh_from_db()

    assert givesome_purse.balance == 0
    assert brand_purse.balance == 200


@pytest.mark.django_db
def test_funds_are_moved_to_brand_purse_disallowed(vendor_user_brand):
    givesome_purse = get_default_purse(supplier=None)
    brand_purse = get_default_purse(supplier=vendor_user_brand.vendor, supplier_purse_allowed=False)
    _create_and_handle_expired_batch(supplier=vendor_user_brand.vendor)

    givesome_purse.refresh_from_db()
    brand_purse.refresh_from_db()

    assert givesome_purse.balance == 200
    assert brand_purse.balance == 0


@pytest.mark.django_db
def test_purse_manual_donation(vendor_user_charity):
    project = vendor_user_charity.project
    purse = get_default_purse(balance=3000)
    allocation = create_givesome_purse_allocation(shop_product=project)
    create_default_order_statuses()

    assert purse.balance == 3000
    assert project.product.project_extra.goal_amount == 1000

    with pytest.raises(ValidationError):
        allocation.create_manual_donation(0)  # Can't donate 0
    with pytest.raises(ValidationError):
        allocation.create_manual_donation(2000)  # Can't donate more than project can accept

    change_project_goal(project, 2000)
    assert project.product.project_extra.goal_amount == 2000

    with pytest.raises(ValidationError):
        allocation.create_manual_donation(4000)  # Can't donate more givesome purse has

    # Valid small donation
    allocation.create_manual_donation(100)
    purse.refresh_from_db()
    assert purse.balance == 2900
    assert project.product.project_extra.goal_progress_amount == 100

    # Valid
    allocation.create_manual_donation(allocation.get_max_donate_amount())
    purse.refresh_from_db()
    assert purse.balance == 1000  # Purse (3000) - project goal (2000)
    assert project.product.project_extra.goal_progress_amount == 2000

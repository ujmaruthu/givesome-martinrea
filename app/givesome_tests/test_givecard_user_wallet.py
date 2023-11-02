# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from datetime import timedelta
from uuid import uuid4

import pytest
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from shuup.testing.factories import create_random_user

from givesome.enums import GivecardDonateRestrictionType
from givesome.front.views.givecard_wallet import group_givecards_in_wallet
from givesome.models import Givecard
from givesome_tests.factories import givecard_batch_factory, givecard_campaign_factory, givecard_factory


class MockWalletRequest:
    def __init__(self):
        self.session = {"givecard_wallet": {}}
        self.user = AnonymousUser()


@pytest.mark.django_db
def test_group_givecards_in_wallet_by_campaign():
    campaign1 = givecard_campaign_factory(name="campaign-1")
    campaign2 = givecard_campaign_factory(name="campaign-2")
    campaign3 = givecard_campaign_factory(name="campaign-3")
    batch1 = givecard_batch_factory(campaign=campaign1)
    batch2 = givecard_batch_factory(campaign=campaign2)
    batch3 = givecard_batch_factory(campaign=campaign3)
    givecards = [
        givecard_factory(batch=batch1, balance=10),
        givecard_factory(batch=batch2, balance=10),
        givecard_factory(batch=batch2, balance=10),
        givecard_factory(batch=batch3, balance=5),
        givecard_factory(batch=batch3, balance=2),
        givecard_factory(batch=batch3, balance=2),
    ]

    request = MockWalletRequest()
    for givecard in givecards:
        request.session["givecard_wallet"][givecard.get_code()] = givecard.get_data_for_wallet()

    assert request.user.is_anonymous is True
    # First run test with anonymous user, then with an authenticated user. Same results are expected
    for i in range(0, 2):
        wallet = group_givecards_in_wallet(request)

        assert len(wallet) == 3  # 3 types of campaigns

        assert len(wallet[campaign1.pk][0][0]) == 1  # 1 type of balance
        assert wallet[campaign1.pk][0][0][10]["count"] == 1
        assert wallet[campaign1.pk][0][0][10]["campaign"] == 1
        assert wallet[campaign1.pk][0][0][10]["campaign_name"] == "campaign-1"

        assert len(wallet[campaign2.pk][0][0]) == 1  # 1 type of balance
        assert wallet[campaign2.pk][0][0][10]["count"] == 2

        assert len(wallet[campaign3.pk][0][0]) == 2  # 2 type of balance
        assert wallet[campaign3.pk][0][0][5]["count"] == 1
        assert wallet[campaign3.pk][0][0][2]["count"] == 2

        # Change user to authenticated, redeem givecards for user
        if i == 0:
            user = create_random_user(username=uuid4())
            request.user = user
            Givecard.objects.all().update(user=user)
    assert request.user.is_anonymous is False


@pytest.mark.django_db
def test_group_givecards_in_wallet_by_balance():
    campaign = givecard_campaign_factory(name="campaign-1")
    batch = givecard_batch_factory(campaign=campaign)
    givecards = [
        givecard_factory(batch=batch, balance=10),
        givecard_factory(batch=batch, balance=10),
        givecard_factory(batch=batch, balance=10),
        givecard_factory(batch=batch, balance=5),
        givecard_factory(batch=batch, balance=2),
        givecard_factory(batch=batch, balance=2),
    ]

    request = MockWalletRequest()
    for givecard in givecards:
        request.session["givecard_wallet"][givecard.get_code()] = givecard.get_data_for_wallet()

    assert request.user.is_anonymous is True
    # First run test with anonymous user, then with an authenticated user. Same results are expected
    for i in range(0, 2):
        wallet = group_givecards_in_wallet(request)

        assert len(wallet[1]) == 1  # Only 1 type of suppliers (none)
        assert len(wallet[1][0]) == 1  # Only 1 type of offices (none)
        assert len(wallet[1][0][0]) == 3  # 3 types of balances
        assert wallet[1][0][0][10]["count"] == 3  # 3 $10 cards in wallet
        assert wallet[1][0][0][2]["count"] == 2
        assert wallet[1][0][0][2]["balance"] == 2

        # Change user to authenticated, redeem givecards for user
        if i == 0:
            user = create_random_user(username=uuid4())
            request.user = user
            Givecard.objects.all().update(user=user)
    assert request.user.is_anonymous is False


@pytest.mark.django_db
def test_group_givecards_in_wallet_by_supplier_and_office(vendor_user_brand, vendor_user_brand_2):
    supplier = vendor_user_brand.vendor
    supplier2 = vendor_user_brand_2.vendor
    office = vendor_user_brand.office
    office2 = vendor_user_brand.office2
    chapter = vendor_user_brand_2.office
    campaign = givecard_campaign_factory(name="campaign-1")
    batch_no_supplier = givecard_batch_factory(campaign=campaign)
    batch_supplier = givecard_batch_factory(campaign=campaign, supplier=supplier)
    batch_supplier2 = givecard_batch_factory(campaign=campaign, supplier=supplier2)
    batch_office = givecard_batch_factory(campaign=campaign, supplier=supplier, office=office)
    batch_office2 = givecard_batch_factory(campaign=campaign, supplier=supplier, office=office2)
    batch_chapter = givecard_batch_factory(campaign=campaign, supplier=supplier2, office=chapter)
    givecards = [
        givecard_factory(batch=batch_no_supplier, balance=10),
        givecard_factory(batch=batch_supplier, balance=10),
        givecard_factory(batch=batch_supplier2, balance=10),
        givecard_factory(batch=batch_office, balance=10),
        givecard_factory(batch=batch_office2, balance=10),
        givecard_factory(batch=batch_chapter, balance=10),
    ]

    request = MockWalletRequest()
    for givecard in givecards:
        request.session["givecard_wallet"][givecard.get_code()] = givecard.get_data_for_wallet()

    assert request.user.is_anonymous is True
    # First run test with anonymous user, then with an authenticated user. Same results are expected
    for i in range(0, 2):
        wallet = group_givecards_in_wallet(request)
        assert len(wallet[1]) == 3  # None + 2 suppliers = 3
        assert len(wallet[1][0][0]) == 1  # Givecards without supplier or office
        assert len(wallet[1][supplier.pk][0]) == 1  # Givecards with supplier 1 but no offices
        assert len(wallet[1][supplier.pk][office.pk]) == 1  # Givecards with supplier 1 and office 1
        assert len(wallet[1][supplier.pk][office2.pk]) == 1
        assert len(wallet[1][supplier2.pk][0]) == 1
        assert len(wallet[1][supplier2.pk][chapter.pk]) == 1
        assert wallet[1][supplier.pk][office.pk][10]["supplier"] == supplier.pk
        assert wallet[1][supplier.pk][office.pk][10]["supplier_name"] == supplier.name
        assert wallet[1][supplier.pk][office.pk][10]["office"] == office.pk
        assert wallet[1][supplier.pk][office.pk][10]["office_name"] == office.name
        assert office.pk not in wallet[1][supplier2.pk]  # Supplier and office mismatch

        # Change user to authenticated, redeem givecards for user
        if i == 0:
            user = create_random_user(username=uuid4())
            request.user = user
            Givecard.objects.all().update(user=user)
    assert request.user.is_anonymous is False


@pytest.mark.django_db
def test_group_givecards_in_wallet_exp_dates():
    today = timezone.localdate()
    day = timedelta(days=1)
    campaign = givecard_campaign_factory(name="campaign-1")
    batch_no_exp = givecard_batch_factory(campaign=campaign)
    batch_exp_future = givecard_batch_factory(campaign=campaign, expiration_date=today + day * 10)
    batch_exp_soon = givecard_batch_factory(campaign=campaign, expiration_date=today + day * 3)
    batch_exp_sooner = givecard_batch_factory(campaign=campaign, expiration_date=today + day * 2)
    givecards = [
        givecard_factory(batch=batch_no_exp, balance=1),
        givecard_factory(batch=batch_exp_future, balance=2),
        givecard_factory(batch=batch_exp_soon, balance=3),
        givecard_factory(batch=batch_exp_soon, balance=4),
        givecard_factory(batch=batch_exp_sooner, balance=4),
        givecard_factory(batch=batch_exp_soon, balance=4),
    ]

    request = MockWalletRequest()
    for givecard in givecards:
        request.session["givecard_wallet"][givecard.get_code()] = givecard.get_data_for_wallet()

    assert request.user.is_anonymous is True
    # First run test with anonymous user, then with an authenticated user. Same results are expected
    for i in range(0, 2):
        wallet = group_givecards_in_wallet(request)
        assert len(wallet[1]) == 1  # Only 1 type of suppliers (none)
        assert len(wallet[1][0][0]) == 4

        # Not expiring
        assert "exp_date" not in wallet[1][0][0][1]

        # Exp date far away in the future
        assert "exp_date" in wallet[1][0][0][2]
        assert wallet[1][0][0][2]["is_expiring_soon"] is False
        assert wallet[1][0][0][2]["exp_date"] == today + day * 10  # Correct expiry date set

        # Exp date in under a week (is expiring soon)
        assert "exp_date" in wallet[1][0][0][3]
        assert wallet[1][0][0][3]["is_expiring_soon"] is True
        assert wallet[1][0][0][3]["exp_date"] == today + day * 3  # Correct expiry date set

        # Expiring soon, but group has two different expiry dates
        assert "exp_date" in wallet[1][0][0][4]
        assert wallet[1][0][0][4]["is_expiring_soon"] is True
        assert wallet[1][0][0][4]["exp_date"] == today + day * 2  # Two exp dates, but earlier is expected
        assert wallet[1][0][0][4]["exp_balance"] == 4  # Balance is also correct

        # Change user to authenticated, redeem givecards for user
        if i == 0:
            user = create_random_user(username=uuid4())
            request.user = user
            Givecard.objects.all().update(user=user)
    assert request.user.is_anonymous is False


@pytest.mark.django_db
def test_group_givecards_in_wallet_restriction_types(vendor_user_brand):
    supplier = vendor_user_brand.vendor
    office = vendor_user_brand.office
    office2 = vendor_user_brand.office2
    campaign = givecard_campaign_factory(name="campaign-1")

    batch1 = givecard_batch_factory(
        campaign=campaign, supplier=supplier, office=office, restriction_type=GivecardDonateRestrictionType.SUPPLIER
    )
    batch2 = givecard_batch_factory(
        campaign=campaign, supplier=supplier, office=office2, restriction_type=GivecardDonateRestrictionType.DISABLED
    )
    batch3 = givecard_batch_factory(
        campaign=campaign, supplier=supplier, restriction_type=GivecardDonateRestrictionType.DISABLED
    )
    batch4 = givecard_batch_factory(
        campaign=campaign, supplier=supplier, office=office, restriction_type=GivecardDonateRestrictionType.OFFICE
    )

    givecards = [
        givecard_factory(batch=batch1, balance=10),
        givecard_factory(batch=batch2, balance=10),
        givecard_factory(batch=batch3, balance=10),
        givecard_factory(batch=batch4, balance=10),
    ]

    request = MockWalletRequest()
    for givecard in givecards:
        request.session["givecard_wallet"][givecard.get_code()] = givecard.get_data_for_wallet()

    assert request.user.is_anonymous is True
    # First run test with anonymous user, then with an authenticated user. Same results are expected
    for i in range(0, 2):
        wallet = group_givecards_in_wallet(request)
        assert len(wallet[1]) == 2  # 2 types of suppliers (one actual + none)
        assert wallet[1][0][0][10]["count"] == 2  # 2 $10 cards in wallet with disabled restrictions
        assert wallet[1][supplier.pk][0][10]["count"] == 1  # Office defined, but Supplier level restriction
        assert wallet[1][supplier.pk][office.pk][10]["count"] == 1  # Office defined and office level restriction

        # Change user to authenticated, redeem givecards for user
        if i == 0:
            user = create_random_user(username=uuid4())
            request.user = user
            Givecard.objects.all().update(user=user)
    assert request.user.is_anonymous is False

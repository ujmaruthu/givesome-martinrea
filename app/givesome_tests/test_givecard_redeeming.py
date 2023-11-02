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
from django.core.exceptions import ValidationError
from django.utils import timezone
from shuup.testing.factories import create_random_user

from givesome.enums import GivecardDonateRestrictionType
from givesome.models import Givecard, GivecardBatch
from givesome_tests import settings
from givesome_tests.factories import givecard_batch_factory, givecard_campaign_factory, givecard_factory


# Givecard methods
@pytest.mark.django_db
def test_givecard_is_redeemable_with_and_without_campaign():
    givecard = givecard_factory()
    batch = givecard.batch

    # No campaign, not redeemable
    assert givecard.is_redeemable() is False

    # Has campaign and nothing else prevents redeeming
    batch.campaign = givecard_campaign_factory()
    batch.save()
    assert givecard.is_redeemable() is True


@pytest.mark.django_db
def test_givecard_is_redeemable_dates():
    givecard = givecard_factory(campaign=givecard_campaign_factory())
    assert givecard.is_redeemable() is True
    batch = givecard.batch
    now = timezone.localdate()
    day = timedelta(days=1)

    # Givecard redemption has not started yet
    batch.redemption_start_date = now + day
    batch.save()
    assert givecard.is_redeemable() is False
    assert batch.is_redeemable() is False

    # Givecard redemption has ended
    batch.redemption_start_date = None
    batch.redemption_end_date = now - day
    batch.save()
    assert givecard.is_redeemable() is False
    assert batch.is_redeemable() is False

    # Givecard is expired
    batch.redemption_end_date = None
    batch.expiration_date = now - day
    batch.save()
    assert givecard.is_redeemable() is False
    assert batch.is_redeemable() is False

    # With all dates set and valid
    batch.redemption_start_date = now - day  # Started
    batch.redemption_end_date = now + day  # Not ended
    batch.expiration_date = now + day  # Not expired
    batch.save()
    assert givecard.is_redeemable() is True
    assert batch.is_redeemable() is True


@pytest.mark.django_db
def test_multicard_is_redeemable_again_by_same_user():
    user = create_random_user(username=uuid4())
    user2 = create_random_user(username=uuid4())
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=10, code="AAAAAA").generate_givecards()

    # First time is ok
    assert batch.get_best_multicard().redeem(user)

    # Second time trying to redeem results in error
    with pytest.raises(ValidationError):
        assert batch.get_best_multicard().redeem(user)

    # Someone else can redeem it
    assert batch.get_best_multicard().redeem()
    assert batch.get_best_multicard().redeem(user2)


@pytest.mark.django_db
def test_unique_givecard_batch_is_redeemable_again_by_same_user():
    user = create_random_user(username=uuid4())
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=10).generate_givecards()

    # All Givecards can be redeemed by the same user
    for i in range(1, 10):
        # Redeem every Givecard in Batch (not the same Givecard over and over again)
        batch.givecards.redeemable().first().redeem(user)


@pytest.mark.django_db
def test_unique_givecard_is_redeemable_already_claimed():
    givecard = givecard_factory(campaign=givecard_campaign_factory())

    # Not claimed, redeemable
    assert givecard.is_redeemable() is True

    # Redeemed by Anonymous user, still redeemable as its not claimed
    assert givecard.redeem()
    assert givecard.user is None
    assert givecard.redeemed_on is not None

    # Not redeemable after someone claimed it
    givecard.redeem(user=create_random_user(username=uuid4()))  # Does not raise an error
    assert givecard.user is not None
    assert givecard.redeemed_on is not None
    assert givecard.is_redeemable() is False

    # Not redeemable after someone claimed it
    with pytest.raises(ValidationError):
        givecard.redeem()


@pytest.mark.django_db
def test_unique_givecard_is_redeemable_balance():
    givecard = givecard_factory(campaign=givecard_campaign_factory(), balance=10)

    # Full balance, redeemable
    assert givecard.is_redeemable() is True

    # Balance is partially used, still valid to redeem
    givecard.balance = 5
    givecard.save()
    assert givecard.is_redeemable() is True

    # Balance is zero, not redeemable anymore
    givecard.balance = 0
    givecard.save()
    assert givecard.is_redeemable() is False


# Batch methods
@pytest.mark.django_db
def test_batch_is_redeemable_campaign():
    # Not redeemable when it has no givecards
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=10)
    assert batch.is_redeemable() is False
    batch.generate_givecards()
    assert batch.is_redeemable() is True

    batch.campaign = None
    batch.save()
    assert batch.is_redeemable() is False


@pytest.mark.django_db
def test_batch_is_redeemable_already_claimed():
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=2)
    batch.generate_givecards()
    assert batch.is_redeemable() is True

    Givecard.objects.update(user=create_random_user(username=uuid4()))
    assert batch.is_redeemable() is False

    givecard = Givecard.objects.first()
    givecard.user = None
    givecard.save()
    assert batch.is_redeemable() is True


@pytest.mark.django_db
def test_batch_redeem():
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=2, code="AAAAAA")
    batch.generate_givecards()

    # Batch is redeemable
    givecard = batch.redeem()
    assert givecard.__class__ == Givecard
    assert givecard.user is None
    assert givecard.redeemed_on is not None

    # Batch is still redeemable
    givecard = batch.redeem(create_random_user(username=uuid4()))
    assert givecard.user is not None
    assert givecard.redeemed_on is not None

    # No more multicards redeemable, raises an error
    with pytest.raises(ValidationError):
        batch.redeem()

    # Non-givecard batches ca not be redeemed
    givecard = givecard_factory(campaign=givecard_campaign_factory())
    with pytest.raises(ValidationError):
        givecard.batch.redeem()


@pytest.mark.django_db
def test_batch_is_redeemable_balance():
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=2)
    batch.generate_givecards()
    assert batch.is_redeemable() is True

    Givecard.objects.update(balance=0)
    assert batch.is_redeemable() is False

    givecard = Givecard.objects.first()
    givecard.balance = 2
    givecard.save()
    assert batch.is_redeemable() is True


@pytest.mark.django_db
def test_batch_is_redeemable_supplier_brand_page_is_disabled(vendor_user_brand):
    extra = vendor_user_brand.vendor.givesome_extra
    extra.allow_brand_page = False
    extra.save()
    batch = givecard_batch_factory(
        campaign=givecard_campaign_factory(),
        supplier=vendor_user_brand.vendor,
        restriction_type=GivecardDonateRestrictionType.OFFICE,
    )
    batch.generate_givecards()
    assert batch.is_redeemable() is False

    extra.allow_brand_page = True
    extra.save()
    assert batch.is_redeemable() is True


@pytest.mark.django_db
def test_batch_redeemable_filter_dates():
    givecard = givecard_factory(campaign=givecard_campaign_factory())
    batch = givecard.batch
    now = timezone.localdate()
    day = timedelta(days=1)
    assert Givecard.objects.redeemable().count() == 1
    assert GivecardBatch.objects.redeemable().count() == 1

    # Givecard redemption has not started yet
    batch.redemption_start_date = now + day
    batch.save()

    # Givecard redemption has ended
    batch.redemption_start_date = None
    batch.redemption_end_date = now - day
    batch.save()
    assert Givecard.objects.redeemable().count() == 0
    assert GivecardBatch.objects.redeemable().count() == 0

    # Givecard is expired
    batch.redemption_end_date = None
    batch.expiration_date = now - day
    batch.save()
    assert Givecard.objects.redeemable().count() == 0
    assert GivecardBatch.objects.redeemable().count() == 0

    # With all dates set and valid
    batch.redemption_start_date = now - day  # Started
    batch.redemption_end_date = now + day  # Not ended
    batch.expiration_date = now + day  # Not expired
    batch.save()
    assert Givecard.objects.redeemable().count() == 1
    assert GivecardBatch.objects.redeemable().count() == 1


@pytest.mark.django_db
def test_batch_get_best_givecard_based_on_balance():
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=5, value=5)
    batch.generate_givecards()

    # No Multicards claimed, highest value one returned
    givecard = batch.givecards.first()
    givecard.balance = 6
    givecard.save()
    assert batch.get_best_multicard().id == givecard.id

    # Lower balance card is not returned
    givecard.balance = 4
    givecard.save()
    assert batch.get_best_multicard().id != givecard.id


@pytest.mark.django_db
def test_batch_get_best_givecard_based_on_redeemed_on():
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=5)
    batch.generate_givecards()

    # All Multicards have been redeemed but not claimed, return the oldest
    for i, givecard in enumerate(batch.givecards.all()):
        givecard.redeemed_on = timezone.localtime() - timedelta(days=i)
        givecard.save()
    oldest = Givecard.objects.order_by("redeemed_on").first()
    assert batch.get_best_multicard().id == oldest.id

    # Non-redeemed is prioritised
    non_redeemed = batch.givecards.first()
    non_redeemed.redeemed_on = None
    non_redeemed.save()
    assert batch.get_best_multicard().id == non_redeemed.id

    # Non-redeemed is prioritised, even when a card has higher value
    oldest.balance = 10
    oldest.save()
    assert batch.get_best_multicard().id == non_redeemed.id


# Queryset methods
@pytest.mark.django_db
def test_batch_redeemable_filter():
    # No redeemable Givecards
    batch = givecard_batch_factory(amount=10).generate_givecards()
    assert GivecardBatch.objects.redeemable().count() == 0

    # Batch has campaign, becomes valid
    batch.campaign = givecard_campaign_factory()
    batch.save()
    assert GivecardBatch.objects.redeemable().count() == 1

    # Already claimed
    givecard = batch.givecards.first()
    givecard.user = create_random_user(username=uuid4())
    givecard.save()
    assert GivecardBatch.objects.redeemable().count() == 1
    batch.givecards.update(user=create_random_user(username=uuid4()))
    assert GivecardBatch.objects.redeemable().count() == 0

    # No balance
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=10).generate_givecards()
    assert GivecardBatch.objects.redeemable().count() == 1
    givecard = batch.givecards.first()
    givecard.balance = 0
    givecard.save()
    assert GivecardBatch.objects.redeemable().count() == 1
    batch.givecards.update(balance=0)
    assert GivecardBatch.objects.redeemable().count() == 0

    # Redeemed recently
    batch = givecard_batch_factory(campaign=givecard_campaign_factory(), amount=10).generate_givecards()
    assert GivecardBatch.objects.redeemable().count() == 1
    givecard = batch.givecards.first()
    givecard.redeemed_on = timezone.localtime()
    givecard.save()
    assert GivecardBatch.objects.redeemable().count() == 1
    batch.givecards.update(redeemed_on=timezone.localtime())
    assert GivecardBatch.objects.redeemable().count() == 0

    # Expired
    givecard_batch_factory(
        campaign=givecard_campaign_factory(), amount=10, expiration_date=timezone.localdate() - timedelta(days=1)
    ).generate_givecards()
    assert GivecardBatch.objects.redeemable().count() == 0


@pytest.mark.django_db
def test_givecard_redeemable_filter():
    # No redeemable Givecards
    givecard_factory()
    assert Givecard.objects.redeemable().count() == 0

    campaign = givecard_campaign_factory()
    # One redeemable Givecard
    givecard_factory(campaign=campaign)
    assert Givecard.objects.redeemable().count() == 1

    # Givecard with user is not redeemable
    givecard_factory(campaign=campaign, user=create_random_user(username=uuid4()))
    assert Givecard.objects.redeemable().count() == 1

    # Unique givecard is redeemable, without grace period
    givecard = givecard_factory(campaign=campaign)
    givecard.redeemed_on = timezone.localtime()
    givecard.save()
    assert Givecard.objects.redeemable().count() == 2

    # Multicard is not redeemable if redeemed recently
    givecard = givecard_factory(batch=givecard_batch_factory(campaign=campaign, code="AAAAAA"))
    givecard.redeemed_on = timezone.localtime()
    givecard.save()
    assert Givecard.objects.redeemable().count() == 2

    # Redeemable after grace period
    grace_period = timezone.localtime() - timedelta(days=settings.GIVESOME_MULTICARD_REDEEM_GRACE_PERIOD_DAYS)
    givecard.redeemed_on = grace_period - timedelta(minutes=1)
    givecard.save()
    assert Givecard.objects.redeemable().count() == 3

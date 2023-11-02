# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import random

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from shuup.testing.factories import get_default_shop, get_faker

from givesome.enums import GivecardBatchExpiryType, GivecardDonateRestrictionType
from givesome.givecard_utils import generate_new_code
from givesome.models import (
    Givecard,
    GivecardBatch,
    GivecardCampaign,
    GivecardPurseCharge,
    GivesomePurse,
    GivesomePurseAllocation,
)


def givecard_campaign_factory(name=None, identifier=None, supplier=None, image=None):
    fake = get_faker(["company", "lorem"])
    name = name if name is not None else f"{fake.company()}-{GivecardCampaign.objects.all().count() + 1}"
    identifier = identifier if identifier is not None else slugify(name)
    message = fake.paragraph(nb_sentences=4)

    campaign = GivecardCampaign.objects.create(
        identifier=identifier, supplier=supplier, name=name, message=message, image=image
    )

    return campaign


def givecard_batch_factory(
    amount=None,
    value=None,
    campaign=None,
    supplier=None,
    office=None,
    code=None,
    redemption_start_date=None,
    redemption_end_date=None,
    expiration_date=None,
    restriction_type=None,
    expiry_type=None,
):
    fake = get_faker(
        [
            "date_time",
        ]
    )
    amount = amount if amount is not None else random.randint(1, 50) * 100
    value = value if value is not None else random.choice([2, 5, 10])
    redemption_start_date = redemption_start_date or fake.date_time_this_decade(before_now=True, after_now=False).date()
    redemption_end_date = redemption_end_date or fake.date_time_this_decade(before_now=False, after_now=True).date()
    expiration_date = expiration_date
    restriction_type = restriction_type if restriction_type is not None else GivecardDonateRestrictionType.OFFICE
    expiry_type = expiry_type if expiry_type is not None else GivecardBatchExpiryType.AUTOMATIC

    batch = GivecardBatch.objects.create(
        campaign=campaign,
        amount=amount,
        value=value,
        code=code,
        supplier=supplier,
        office=office,
        redemption_start_date=redemption_start_date,
        redemption_end_date=redemption_end_date,
        expiration_date=expiration_date,
        restriction_type=restriction_type,
        expiry_type=expiry_type,
    )

    return batch


def givecard_factory(campaign=None, batch=None, user=None, code=None, balance=None):
    if batch is not None and campaign is not None:
        # If both Campaign and Batch are given, given campaign is not used
        raise ValidationError("Entering both Campaign and Batch is not supported")

    batch = batch if batch is not None else givecard_batch_factory(campaign=campaign, amount=1, value=balance)
    balance = balance if balance is not None else batch.value
    code = code if code is not None else generate_new_code()

    givecard = Givecard.objects.create(batch=batch, code=code, balance=balance, user=user)

    return givecard


def get_default_purse(balance=0, supplier=None, supplier_purse_allowed=True):
    purse, __ = GivesomePurse.objects.get_or_create(shop=get_default_shop(), supplier=supplier)
    if balance > 0:
        batch = givecard_batch_factory(amount=1, value=balance)
        batch.generate_givecards()
        GivecardPurseCharge.objects.create(
            purse=purse, batch=batch, charge_amount=batch.total_balance, charge_date=timezone.localtime()
        )
    if supplier is not None and supplier_purse_allowed:
        extra = supplier.givesome_extra
        extra.allow_purse = True
        extra.save()
    purse.refresh_from_db()
    return purse


def create_givesome_purse_allocation(shop_product=None, weight=0, supplier=None):
    if shop_product is None:
        raise ValidationError("shop_product is a required field in GivesomePurseAllocation")

    purse = get_default_purse(supplier=supplier)
    return GivesomePurseAllocation.objects.create(purse=purse, weight=weight, shop_product=shop_product)

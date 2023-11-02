# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from datetime import date, datetime, timedelta
from typing import Optional

from django.utils import timezone
from django.views.generic import TemplateView
from shuup.core.utils import context_cache

from givesome.front.utils import get_promoter_from_request
from givesome.models import Givecard, GivecardQuerySet


def ensure_session_wallet(request):
    if "givecard_wallet" not in request.session:
        request.session["givecard_wallet"] = {}
    return request.session["givecard_wallet"]


def get_cached_wallet(request):
    def _get_session_key(request):
        """Sometimes session_key is None and session needs to be created"""
        if request.session.session_key is None:
            request.session.create()
        return request.session.session_key

    return context_cache.get_cached_value(
        identifier="grouped_givecard_wallet",
        item=None,
        context={},  # User can't be here as this is filtered
        user=request.user,  # User is used when generating cache key
        # User shares same cache even across multiple sessions
        session_key=_get_session_key(request) if request.user.is_anonymous else None,
    )


def bump_wallet_cache(request):
    update_all_givecards_in_wallet(request)
    key, grouped_givecards = get_cached_wallet(request)
    context_cache.set_cached_value(key, group_givecards_in_wallet(request))


def get_givecard_objects_from_wallet(request) -> GivecardQuerySet:
    """
    Returns all Givecards in the user's wallet,
    regardless or not if they have already been redeemed by another user
    """
    wallet = ensure_session_wallet(request)
    session_givecards = [wallet[code]["id"] for code in wallet]
    return Givecard.objects.filter(pk__in=session_givecards)


def get_user_givecards(request) -> GivecardQuerySet:
    if request.user.is_authenticated:
        givecards = Givecard.objects.filter(user=request.user)
    else:
        givecards = get_givecard_objects_from_wallet(request)
    return givecards


def get_usable_givecards(request) -> GivecardQuerySet:
    """
    Helper function to get usable Givecards for post requests

    Uses promoter info, if request contains it

    For anonymous users find givecards based on session wallet codes
    For authenticated users find givecards claimed by request user
    """
    givecards = get_user_givecards(request)

    promoter, __ = get_promoter_from_request(request)

    return givecards.filter_promoter_usable_givecards(promoter)


def group_givecards_in_wallet(request) -> dict:
    """
    Return Givecards ordered and grouped by Campaign, Supplier, Office, Balance

    Expiry related data (`exp_date`, `exp_balance`, `is_expiring_soon`)
    always refer to earliest expiring Givecard(s) in group.
    `exp_date` and `exp_balance` is omitted if there are no expiring Givecards in group

    Uses session storage if user is anonymous, uses data from database if user is authenticated

    Example output might look something like this:
    {
        1: {  # Campaign 1
            0: {  # No supplier
                0: {  # No office
                    10: {'id': 1, 'balance': 10, 'count': 3},
                    5: {'id': 4, 'balance': 5, 'count': 1},
                    2: {'id': 5, 'balance': 2, 'count': 2}
                }
            },
            1: {  # Supplier 1
                0: {  # No office
                    10: {'balance': 10, 'supplier': 1, 'supplier_name': 'Brand Vendor', 'count': 1}
                },
                1: {  # Office 1
                    10: {'balance': 10, 'supplier': 1, 'supplier_name': 'Brand Vendor',
                         'office': 1, 'office_name': 'Office1', 'count': 1}
                }
            }
        }
    }
    """

    def _get_exp_date(givecard: dict) -> Optional[date]:
        """Extract expiry date from givecard dict, which can be a date or str type in some cases"""
        if "exp_date" in givecard:
            exp_date = givecard["exp_date"]
            if isinstance(exp_date, str):
                return datetime.strptime(givecard["exp_date"], "%Y-%m-%d").date()
            return exp_date
        return None

    def _ensure_wallet_groups_exists(grouped_givecards, givecard):
        """Helper function used in grouping givecards in wallet"""
        campaign = givecard["campaign"] if "campaign" in givecard else 0  # 0 = No Campaign, which should be impossible
        supplier = givecard["supplier"] if "supplier" in givecard else 0  # 0 = No supplier
        office = givecard["office"] if "office" in givecard else 0  # 0 = No office

        if campaign not in grouped_givecards:
            grouped_givecards[campaign] = {}
        if supplier not in grouped_givecards[campaign]:
            grouped_givecards[campaign][supplier] = {}
        if office not in grouped_givecards[campaign][supplier]:
            grouped_givecards[campaign][supplier][office] = {}
        return grouped_givecards[campaign][supplier][office]

    def _new_givecard_entry(givecard):
        givecard = dict(givecard)  # Do not modify the original in session storage
        givecard["count"] = 1
        givecard.pop("id", None)  # This won't be needed
        givecard.pop("code", None)  # This won't be needed
        if "exp_date" in givecard:
            givecard["exp_balance"] = givecard["balance"]
        return givecard

    if request is None or request.user.is_anonymous:
        wallet = ensure_session_wallet(request)
        givecards = [wallet[code] for code in wallet]
    else:
        user_givecards = Givecard.objects.usable().filter(user=request.user)
        givecards = [givecard.get_data_for_wallet() for givecard in user_givecards]

    if givecards is None:
        return {}

    grouped_givecards = {}
    for givecard in givecards:
        givecard_date = _get_exp_date(givecard)
        if givecard_date is not None and givecard_date < timezone.localdate() or givecard["balance"] == 0:  # Expired
            continue

        selected_group = _ensure_wallet_groups_exists(grouped_givecards, givecard)

        # First Givecard with same Campaign, Supplier, Office.
        if givecard["balance"] not in selected_group:
            selected_group[givecard["balance"]] = _new_givecard_entry(givecard)

        # Similar Givecard already exists
        else:
            selected_group = selected_group[givecard["balance"]]  # Select existing Givecard
            selected_group["count"] = selected_group["count"] + 1
            if givecard_date is not None:
                if "exp_date" in selected_group:
                    # Same expiry date, add balance to expiring balance
                    if givecard_date == _get_exp_date(selected_group):
                        selected_group["exp_balance"] = selected_group["exp_balance"] + givecard["balance"]
                    # Earlier expiry date so old expiry values are overridden
                    elif givecard_date < _get_exp_date(selected_group):
                        selected_group["exp_date"] = givecard["exp_date"]
                        selected_group["exp_balance"] = givecard["balance"]
                        selected_group["is_expiring_soon"] = givecard["is_expiring_soon"]
                # Similar Givecard exists, but its not expiring. Add current Givecard exp data to group.
                else:
                    selected_group["exp_date"] = givecard["balance"]
                    selected_group["exp_balance"] = givecard["balance"]
                    selected_group["is_expiring_soon"] = givecard["is_expiring_soon"]
    return grouped_givecards


def update_all_givecards_in_wallet(request):
    """
    Cleans session Givecard wallet and repopulates from database
    Updates givecard balances, removes Givecards that are spent or claimed by another user
    """
    wallet = ensure_session_wallet(request)
    user = request.user if not request.user.is_anonymous else None
    givecards = get_user_givecards(request)
    usable_givecards = givecards.usable().filter(user=user)
    used_givecards = (
        givecards.filter(balance=0)
        .filter(user=user, batch__campaign__isnull=False)
        .exclude(batch__expiration_date__lt=timezone.localdate() - timedelta(days=3))
    )

    # Clear wallet to remove any bad data
    wallet.clear()

    # Repopulate wallet from database
    for givecard in usable_givecards:  # Add usable Givecards back to wallet
        wallet[givecard.get_code()] = givecard.get_data_for_wallet()
    for givecard in used_givecards:  # Add any fully used Givecards to wallet to prevent re-redeeming
        wallet[givecard.get_code()] = givecard.get_data_for_wallet()
    request.session.modified = True


class GivecardWalletView(TemplateView):
    template_name = "givesome/shuup/front/givecard_wallet.jinja"

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import django.utils.timezone
import django_jinja
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from parler.utils import get_active_language_choices
from shuup.core.models import Supplier
from shuup.core.templatetags.shuup_common import shuup_static
from shuup.core.utils import context_cache

from givesome.currency_conversion import givesome_exchange_currency
from givesome.front.utils import show_receipting_message
from givesome.front.views.givecard_wallet import ensure_session_wallet, get_cached_wallet, group_givecards_in_wallet
from givesome.models import GivesomeGif


@django_jinja.library.global_function
def get_current_timezone_name() -> str:
    """Return the name of the current timezone, e.g. 'America/Los_Angeles'."""
    return django.utils.timezone.get_current_timezone_name()


@django_jinja.library.global_function
def get_vendor_broad_address(address):
    if not address:
        return []
    lines = [
        address.city,
        address.region,
        address.region_code,
        address.get_country_display(),
    ]
    lines = [line for line in lines if line is not None and line != ""]
    return lines


@django_jinja.library.global_function
def get_givecard_office_or_supplier(givecard):
    """Returns office/supplier id, office/supplier name, url givecard should lead to"""
    if "office" in givecard:
        return (
            givecard["office"],
            givecard["office_name"],
            reverse("office", kwargs={"pk": givecard["office"]}),
        )
    elif "supplier" in givecard:
        supplier = Supplier.objects.filter(pk=givecard["supplier"]).first()
        if supplier is not None:
            return (
                givecard["supplier"],
                givecard["supplier_name"],
                reverse("shuup:supplier", kwargs={"slug": supplier.slug}),
            )
    return None, None, "/"


@django_jinja.library.global_function
def givecard_wallet_total_balance(request) -> int:
    """Calculates wallet total balance"""
    grouped_givecards = get_grouped_givecards(request)
    sum = 0
    if grouped_givecards:
        for campaign in grouped_givecards:
            g = grouped_givecards[campaign]
            for supplier in g:
                for office in g[supplier]:
                    for balance in g[supplier][office]:
                        sum = sum + balance * g[supplier][office][balance]["count"]
    return sum


@django_jinja.library.global_function
def get_grouped_givecards(request) -> dict:
    key, grouped_givecards = get_cached_wallet(request)

    if grouped_givecards is not None:
        return grouped_givecards

    grouped_givecards = group_givecards_in_wallet(request)
    context_cache.set_cached_value(key, grouped_givecards)
    return grouped_givecards


@django_jinja.library.global_function
def get_expiring_givecards(request) -> (int, list):
    wallet = ensure_session_wallet(request)

    today = timezone.localdate()
    givecards = [
        wallet[code]
        for code in wallet
        if wallet[code].get("is_expiring_soon") is True
        and wallet[code]["exp_date"] >= today
        and wallet[code]["balance"] > 0
        and code is not None
    ]
    givecards.sort(key=lambda k: k["exp_date"])  # Order Givecards by expiry date
    expiring_sum = 0
    expiring_givecards = []  # TODO: Cache this?
    for givecard in givecards:
        expiring_sum = expiring_sum + givecard["balance"]
        expiring_givecards.append(givecard)

    return expiring_sum, expiring_givecards


@django_jinja.library.global_function
def get_expiring_givecard_codes(request) -> str:
    wallet = ensure_session_wallet(request)

    today = timezone.localdate()
    codes = [
        code
        for code in wallet
        if wallet[code].get("is_expiring_soon") is True
        and wallet[code]["exp_date"] >= today
        and wallet[code]["balance"] > 0
        and code is not None
    ]
    return ";".join(codes)


@django_jinja.library.global_function
def get_expired_givecards(request) -> list:
    wallet = ensure_session_wallet(request)

    today = timezone.localdate()
    expired_givecards = [
        wallet[code]
        for code in wallet
        if wallet[code].get("is_expiring_soon") is True and wallet[code]["exp_date"] < today
    ]
    expired_givecards.sort(key=lambda k: k["exp_date"])  # Order Givecards by expiry date
    return expired_givecards


@django_jinja.library.global_function
def get_expired_givecard_codes(request) -> str:
    wallet = ensure_session_wallet(request)

    today = timezone.localdate()
    codes = [
        code for code in wallet if wallet[code].get("is_expiring_soon") is True and wallet[code]["exp_date"] < today
    ]
    return ";".join(codes)


@django_jinja.library.global_function
def get_confetti_gif_url():
    checkout_gif = GivesomeGif.objects.filter(active=True).order_by("?").first()
    if checkout_gif and checkout_gif.gif:
        return f"url({checkout_gif.gif.url})"
    return f"url({shuup_static('givesome/img/confetti.gif', 'givesome-marketplace')})"


@django_jinja.library.global_function
def render_receipting_message(message_label: str, charity: Supplier = None) -> str:
    """Replace supported variables with their values if applicable."""
    return show_receipting_message(message_label, charity)


@django_jinja.library.global_function
def recalculate_currency(request, value):
    return givesome_exchange_currency(request.user, value)


@django_jinja.library.global_function
def format_initial_donation(val):
    language = get_active_language_choices()[0]
    if language == "en":
        return f"${val}"
    elif language == "fr-ca":
        return f"{val} $"
    return val


@django_jinja.library.global_function
def givesome_get_firebase_auth_provider_args():
    args = settings.SHUUP_FIREBASE_AUTH_PROVIDER_ARGS
    language = get_active_language_choices()[0]
    if language == "fr-ca":
        args["email"]["fullLabel"] = "S'enregistrer avec l'adresse e-mail"
        args["google"]["fullLabel"] = "Inscrivez-vous avec Google"
    return args


@django_jinja.library.global_function
def format_thank_you_element():
    language = get_active_language_choices()[0]
    if language == "fr-ca":
        return mark_safe('Merci pour votre contribution<br>de <span id="contribution"></span> $ !')
    return mark_safe('Thank you for your $<span id="contribution"></span> contribution!')

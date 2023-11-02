# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from datetime import timedelta

from django.contrib.auth import user_logged_out
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import Product
from shuup.core.signals import stocks_updated
from shuup.notify.base import Event, Variable
from shuup.notify.typology import Email, Integer, Language, Model, Text
from shuup.simple_supplier.models import StockCount
from shuup_multivendor.signals import vendor_shop_product_approval_revoked

from givesome.front.views.givecard_redeem import add_givecard_to_wallet
from givesome.front.views.givecard_wallet import bump_wallet_cache, ensure_session_wallet
from givesome.models import Givecard, GivesomePromotedProduct


class FullyFundedCharity(Event):
    identifier = "project_fully_funded"
    name = _("Project fully funded, Charity")

    product = Variable(_("Project"), type=Model("shuup.product"))
    supplier = Variable(_("Charity"), type=Model("shuup.Supplier"))
    shop_email = Variable(_("Givesome Email"), type=Email)
    supplier_email = Variable(_("Charity Email"), type=Email)
    goal_amount = Variable(_("Goal Amount"), type=Integer)
    fully_funded_date = Variable(_("Fully funded date"), type=Text)
    language = Variable(_("Language"), type=Language)


@receiver(stocks_updated)
def send_project_fully_funded_notification(shops, product_ids, supplier, **kwargs):
    """Sends notifications and handles setting project fully funded date"""
    products = Product.objects.filter(id__in=product_ids)
    for shop in shops:
        for product in products:
            sv = StockCount.objects.filter(supplier_id=supplier, product_id=product.id).first()
            if sv and sv.logical_count <= 0 and hasattr(product, "project_extra"):
                pe = product.project_extra
                if not pe.fully_funded_date and pe.goal_amount > 0:
                    product.project_extra.fully_funded_date = timezone.now().replace(second=0, microsecond=0)
                    product.project_extra.save()
                    # Set backorders to 0 so project cant be donated to any more
                    # after the last donation fills the goal amount
                    shop_product = product.get_shop_instance(shop)
                    shop_product.backorder_maximum = 0
                    shop_product.save()

                    supplier_email = supplier.contact_address.email if supplier.contact_address else ""
                    shop_email = shop.contact_address.email if shop.contact_address else ""
                    FullyFundedCharity(
                        product=product,
                        supplier=supplier,
                        shop_email=shop_email,
                        supplier_email=supplier_email,
                        goal_amount=product.project_extra.goal_amount,
                        fully_funded_date=product.project_extra.fully_funded_date.strftime("%Y-%m-%d"),
                        language=get_language(),
                    ).run(shop=shop)


@receiver(user_logged_in)
def add_givecards_to_user_wallet_on_login(sender, user, request, **kwargs):
    """
    Claim Givecards that were redeemed before logging in

    Also adds recently expired and automatically donated cards to session wallet,
    so we can notify user of their expiry. They will not be shown in wallet anyway
    """
    user_givecards = (
        Givecard.objects.filter(user=user)
        .exclude(batch__expiration_date__lt=timezone.localdate() - timedelta(days=7))
        .filter(Q(balance=0, automatically_donated__gt=0) | Q(balance__gt=0, automatically_donated=0))
        .filter(batch__campaign__isnull=False)
    )
    ensure_session_wallet(request)
    wallet = request.session["givecard_wallet"]
    for code in wallet:
        try:
            givecard = Givecard.objects.filter(pk=wallet[code]["id"]).first()
            if givecard:
                givecard.redeem(user=user)
        except ValidationError:
            pass
    if user_givecards.exists():
        for givecard in user_givecards:
            code = givecard.get_code()
            if code not in wallet:
                add_givecard_to_wallet(givecard, request)
    bump_wallet_cache(request)


@receiver(user_logged_out)
def clear_givecard_wallet_on_logout(sender, user, request, **kwargs):
    """
    Clear old session storage
    Otherwise user is shown their old givecard wallet on logout page
    """
    request.session["givecard_wallet"] = {}


@receiver(vendor_shop_product_approval_revoked)
def remove_project_promotions_on_approval_revoke(shop_product, user, **kwargs):
    shop_product.primary_offices.clear()
    shop_product.primary_suppliers.clear()
    GivesomePromotedProduct.objects.filter(shop_product=shop_product).delete()

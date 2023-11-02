# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import re

from django.core.exceptions import ValidationError
from django.db import OperationalError, ProgrammingError
from django.db.models import Q, QuerySet
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from parler.utils import get_active_language_choices
from shuup.core import cache
from shuup.core.models import ProductMode, ShopProduct, ShopProductVisibility, Supplier
from shuup.core.signals import get_visibility_errors
from shuup.utils.excs import Problem
from shuup_multivendor.utils.product import filter_approved_shop_products

from givesome.models import GivesomeOffice, ReceiptingMessages


def get_promoter_from_request(request):
    """
    Get promoter and promoter type from request
    Only Branded Vendors can be promoters.
    """
    promoter = None
    request_method = request.GET if request.method == "GET" else request.POST
    promoter_type = request_method.get("promoter_type", request_method.get("type", ""))
    promoter_id = None
    if promoter_type:
        try:
            # This will break if user enters non-numbers to the ID parameter
            # Catch any errors and fall back to 'no promoter' instead of breaking hard
            promoter_id = int(request_method.get("promoter_id", request_method.get("id")))
        except (ValueError, TypeError):
            return promoter, promoter_type

    if promoter_type == "GivesomeOffice":
        promoter = GivesomeOffice.objects.filter(id=promoter_id).first()
    elif promoter_type == "Supplier":
        promoter = Supplier.objects.filter(id=promoter_id).first()
        if promoter is None:
            promoter_type = ""
    else:
        # Either there is no promoter or the data is invalid.
        promoter_type = ""
    return promoter, promoter_type


def get_donation_amount_value(donation_amount):
    if donation_amount is None or donation_amount == "":
        raise Problem(_("Error getting donation amount."))

    if '$' in donation_amount:
        raise Problem(_("Do not enter a dollar sign."))
    elif '.' in donation_amount:
        raise Problem(_("Do not enter decimals."))

    donation_amount = donation_amount.replace('$', '').split('.')[0]

    if not donation_amount.isdecimal():  # Contains other than numbers
        raise Problem(_("Please enter an integer amount."))

    try:
        donation_amount = int(donation_amount)
    except ValueError:
        raise Problem(_("You need to enter a number."))

    if donation_amount <= 0:
        raise Problem(_("Please enter a donation amount."))

    return donation_amount


def filter_valid_projects(products: QuerySet, only_always_visible=True, exclude_unapproved=True, promoted=False):
    """
    Return projects that are valid to show for customers
    Includes both active and fully funded projects
    """
    shop_products_set = ShopProduct.objects.filter(
        suppliers__isnull=False, suppliers__deleted=False, product__mode=ProductMode.NORMAL
    )
    if only_always_visible:
        visible_products = shop_products_set.filter(visibility=ShopProductVisibility.ALWAYS_VISIBLE)
        valid_products = visible_products.exclude(
            Q(available_until__lte=now()) | Q(product__project_extra__available_from__gte=now())
        )
        promoted_products = ShopProduct.objects.none()
        if promoted:
            promoted_products = shop_products_set.filter(visibility=ShopProductVisibility.ONLY_VISIBLE_WHEN_PROMOTED)
        shop_products = valid_products | promoted_products
    else:
        # Don't exclude projects that are listed/searchable. Used in e.g. User profile page
        shop_products = shop_products_set.exclude(visibility=ShopProductVisibility.NOT_VISIBLE)

    if exclude_unapproved:
        product_ids = filter_approved_shop_products(shop_products).values_list("product__id", flat=True)
    else:
        product_ids = shop_products.values_list("product__id", flat=True)

    products = products.filter(id__in=product_ids, project_extra__isnull=False).exclude(deleted=True)
    return products


def get_shop_product_visibility_errors(shop_product, customer):
    """Overwrite `shop_product.get_visibility_errors` method to modify `available_until` logic"""
    if shop_product.product.deleted:
        yield ValidationError(_("This product has been deleted."), code="product_deleted")

    if customer and customer.is_all_seeing:  # None of the further conditions matter for omniscient customers.
        return

    if not shop_product.visible:
        yield ValidationError(_("This product is not visible."), code="product_not_visible")

    # If project is fully funded, the page should normally be visible for users even
    # though available_from or available_until dates aren't valid
    extra = shop_product.product.project_extra
    if not (extra.fully_funded_date and shop_product.visibility != ShopProductVisibility.NOT_VISIBLE):
        if shop_product.available_until and shop_product.available_until <= now():
            yield ValidationError(
                _("Error! This product is not available until the current date."), code="product_not_available"
            )
        elif extra.available_from and extra.available_from >= now():
            yield ValidationError(
                _("Error! This product is not available before the current date."), code="product_not_available"
            )

    for receiver, response in get_visibility_errors.send(ShopProduct, shop_product=shop_product, customer=customer):
        for error in response:
            yield error


def show_receipting_message(message_label: str, charity: Supplier = None) -> str:
    """Replace supported variables with their values if applicable."""
    language = get_active_language_choices()[0]
    messages = cache.get(ReceiptingMessages.identifier)
    if not messages:
        try:
            messages = ReceiptingMessages.objects.prefetch_related("translations").first()
        except ProgrammingError:
            # The donation forms use this function to set a field label. This means this function is executed
            # during the build process, which causes problems with migration if ReceiptingMessages hasn't been
            # migrated yet.
            return ""
        except OperationalError:
            # Same issue, but for the unit tests
            return ""
        cache.set(ReceiptingMessages.identifier, messages)

    messages.set_current_language(language)
    try:
        message = getattr(messages, message_label, "")
    except ProgrammingError:
        # If the model changes, an error will be raised by migration.
        return ""
    except OperationalError:
        # Same issue, but for the unit tests
        return ""

    if charity is not None and charity.contact_address is not None:
        country = charity.contact_address.country
        return (
            message.replace("CHARITY_NAME", charity.name)
            .replace("REGISTRATION_NUMBER", charity.givesome_extra.registration_number or "")
            .replace("CHARITY_COUNTRY", country.alpha3 if country.alpha3 == "USA" else country.name)
        )
    else:
        # FIXME: this should be evaluated and implement whitelisting instead.
        if ">" in message or "<" in message:
            message = re.sub("[<>]", "", message)
        return message

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.conf import settings
from django.http import JsonResponse
from shuup.core import cache
from shuup.core.models import Order, OrderLineType, OrderStatus, Payment, ProductMode
from shuup.core.shop_provider import get_shop
from shuup.front.checkout import VerticalCheckoutProcess
from shuup.front.views.checkout import CheckoutViewWithLoginAndRegister
from shuup.utils.money import Money
from shuup_stripe_multivendor.views.payment import HandlePaymentMethodView

from givesome.currency_conversion import convert_to_shop_currency, givesome_exchange_currency
from givesome.enums import DonationType
from givesome.front.checkout import GivesomeGivecardCheckoutPhase, GivesomeStripeCheckoutPhase
from givesome.front.receipting_checkout_state import set_receipting_session_info
from givesome.front.utils import get_donation_amount_value, get_promoter_from_request
from givesome.front.views.givecard_wallet import bump_wallet_cache, get_usable_givecards
from givesome.models import Givecard, PurchaseReportData
from shuup.notify.models import Notification
import datetime
from shuup.notify.enums import RecipientType
if settings.SHUUP_BASKET_CLASS_SPEC == "shuup_multivendor.basket.MultivendorBasket":
    phase_specs = [
        "shuup.front.checkout.checkout_method:CheckoutMethodPhase",
        "shuup.front.checkout.checkout_method:RegisterPhase",
        "shuup.front.checkout.addresses:AddressesPhase",
        "shuup.front.checkout.methods:MethodsPhase",
        "shuup_multivendor.checkout:MultivendorMethodsPhase",
        "shuup_multivendor.checkout:MultivendorShippingMethodSpawnerPhase",
        "shuup.front.checkout.methods:PaymentMethodPhase",
        "shuup.front.checkout.confirm:ConfirmPhase",
    ]
else:
    phase_specs = [
        "shuup.front.checkout.checkout_method:CheckoutMethodPhase",
        "shuup.front.checkout.checkout_method:RegisterPhase",
        "shuup.front.checkout.addresses:AddressesPhase",
        "shuup.front.checkout.methods:MethodsPhase",
        "shuup.front.checkout.methods:ShippingMethodPhase",
        "shuup.front.checkout.methods:PaymentMethodPhase",
        "shuup.front.checkout.confirm:ConfirmPhase",
    ]


class CheckoutViewWithLoginAndRegisterVertical(CheckoutViewWithLoginAndRegister):
    process_class = VerticalCheckoutProcess
    phase_specs = phase_specs


class GivesomePaymentView(HandlePaymentMethodView):
    checkout_phase = None
    payment_method = None

    @staticmethod
    def _get_payment_amount(request):
        return get_donation_amount_value(request.POST.get("amt"))

    @staticmethod
    def _collect_base_reporting_data(request, project):
        """Collect various data points required for reports"""
        (promoter, promoter_type) = get_promoter_from_request(request)
        promoting_brand = None
        if promoter_type == "Supplier":
            promoting_brand = promoter
        elif promoter_type == "GivesomeOffice":
            promoting_brand = promoter.supplier

        return {
            "project": project,
            "donation_type": DonationType.ONE_TIME if project.mode == ProductMode.NORMAL else DonationType.SUBSCRIPTION,
            "promoting_office": promoter if promoter_type == "GivesomeOffice" else None,
            "promoting_brand": promoting_brand,
            "receipt": bool(request.POST.get("receipt")),
        }

    @staticmethod
    def _collect_payment_reporting_data(payments):
        raise NotImplementedError

    def _create_order_payment(self, request, order):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        order = Order.objects.get(pk=request.POST.get("order_id"))
        project = order.lines.filter(type=OrderLineType.PRODUCT).first().product

        # Create payment for order
        payments = self._create_order_payment(request, order)

        # Update order status
        order.update_payment_status()
        order.status = OrderStatus.objects.get_default_complete()
        order.save()

        # Record purchase data
        base_data = self._collect_base_reporting_data(request, project)
        payment_data = self._collect_payment_reporting_data(payments)
        PurchaseReportData.create_rows({**base_data, **payment_data})
        # Clear any receipting tracking from the session
        set_receipting_session_info(request, want_receipt=None)

        # Inform the caller of success by reporting the new totals.
        givecards = get_usable_givecards(self.request)
        promoter = base_data.get("promoting_office") or base_data.get("promoting_brand")

        # Bump cache of all xtheme plugins to show the new Raised amount on projects
        # TODO bump only product plugins cache
        cache.bump_version("shuup_xtheme_cell")

        if project.project_extra.goal_progress_percentage == 100:
            try:
                notifi = Notification()
                notifi.marked_read = False
                notifi.recipient_id = request.user.id
                notifi.shop_id = get_shop(request).id
                notifi.recipient_type = RecipientType.SPECIFIC_USER
                notifi.priority = 2
                notifi.created_on = datetime.datetime.now()
                notifi.message = str(project)+" has been fully funded"
                notifi.save()
            except Exception as e:
                print(e)
        return JsonResponse(
            {
                "new_current_amt": project.project_extra.goal_progress_amount,
                "new_current_amt_preferred_currency": givesome_exchange_currency(
                    self.request.user, project.project_extra.goal_progress_amount
                ),
                "new_current_percent": project.project_extra.goal_progress_percentage,
                "order_id": order.id,
                "givecard_donation_possible": givecards.is_checkout_possible(promoter=promoter),
            }
        )


class GivesomeStripePaymentView(GivesomePaymentView):
    checkout_phase = GivesomeStripeCheckoutPhase
    payment_method = "stripe"

    @staticmethod
    def _collect_payment_reporting_data(payments: Payment):
        return {"payment": payments}  # Payments is a singular payment when Stripe is used

    def _create_order_payment(self, request, order):
        """The user is donating in their own currency, but Givesome accepts CAD. So, calculate the equivalent based
        on today's exchange rates.
        """
        amount = self._get_payment_amount(request)
        converted_amount = convert_to_shop_currency(request.user, amount)
        return order.create_payment(
            Money(value=converted_amount, currency=get_shop(request).currency),
            description=f"Stripe Payment for Donation #{order.id}",
        )


class GivesomeGivecardPaymentView(GivesomePaymentView):
    checkout_phase = GivesomeGivecardCheckoutPhase
    payment_method = "givecard"

    @staticmethod
    def _collect_payment_reporting_data(payments: [(Payment, Givecard)]):
        return {"givecard_payments": payments}  # create_rows creates separate log for every Givecard and Payment

    def _create_order_payment(self, request, order) -> [(Payment, Givecard)]:
        amount = self._get_payment_amount(request)
        converted_amount = convert_to_shop_currency(request.user, amount)
        givecards = get_usable_givecards(request).order_for_checkout()

        used_givecards = []
        for givecard in givecards:
            if converted_amount == 0:  # Order is fully paid
                break

            payment_amount = min(converted_amount, givecard.balance)

            code = givecard.get_code()
            payment = order.create_payment(
                Money(value=payment_amount, currency=get_shop(request).currency),
                description=f"Givecard ({code}) Payment for Donation #{order.id}",
            )
            converted_amount = converted_amount - payment_amount
            givecard.balance = givecard.balance - payment_amount
            givecard.save()
            used_givecards.append((payment, givecard))

        bump_wallet_cache(request)
        return used_givecards

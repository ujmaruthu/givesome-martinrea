# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import stripe
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.forms import BooleanField, ChoiceField, CharField, RadioSelect, forms
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from shuup.core.basket import get_basket_order_creator
from shuup.core.basket.objects import Basket
from shuup.core.models import (
    OrderStatus,
    PaymentMethod,
    ProductMode,
    ShopProduct,
    ShopProductVisibility,
    get_person_contact,
)
from shuup.core.shop_provider import get_shop
from shuup.front.checkout import CheckoutPhaseViewMixin
from shuup.front.signals import checkout_complete
from shuup.utils.excs import Problem
from shuup_stripe_multivendor.models import StripeMultivendorPaymentProcessor
from shuup_stripe_multivendor.utils.customer import ensure_customer

from givesome.admin_module.forms.shop_settings import get_donation_amount_options
from givesome.currency_conversion import convert_to_shop_currency, get_preferred_currency, givesome_exchange_currency
from givesome.front.receipting_checkout_state import user_is_eligible, wants_receipt
from givesome.front.utils import get_donation_amount_value, get_promoter_from_request, show_receipting_message
from givesome.front.views.givecard_wallet import bump_wallet_cache, get_usable_givecards, get_user_givecards
from givesome.models import GivecardPaymentProcessor, GivecardQuerySet
from givesome.models.locale import DonationExtra


class GivesomeDonationForm(forms.Form):
    suffix = ""

    def __init__(self, *args, **kwargs):
        shop = kwargs.pop("shop")
        super().__init__(*args, **kwargs)
        amount_choices = [(amount.value_int, f"${amount.value_int}") for amount in get_donation_amount_options(shop)]
        amount_choices.append((0, _("Other Amount")))
        self.fields["amount" + self.suffix] = ChoiceField(
            widget=RadioSelect(attrs={"class": ""}), choices=amount_choices, required=True
        )
        self.fields["custom" + self.suffix] = CharField(min_length=1, required=False, label=_("Other Amount"))

    def is_valid(self):
        """Accept any positive integer even if not in the list of original choices."""
        amount_key = f"amount{self.suffix}"
        amount = get_donation_amount_value(self.data[amount_key])
        original_choices = [amt[0] for amt in self.fields["amount" + self.suffix].choices]
        if amount not in original_choices:
            updated_choices = self.fields["amount" + self.suffix].choices[:-1]
            updated_choices.append((int(amount), _("Other Amount")))
            self.fields["amount" + self.suffix].choices = updated_choices
        return super().is_valid()


class GivesomeStripeDonationForm(GivesomeDonationForm):
    suffix = ""
    receipt = BooleanField(help_text="", required=False)

    def __init__(self, *args, **kwargs):
        self.charity = kwargs.pop("charity", None)
        receipt = kwargs.pop("wants_receipt", None)
        receipting_enabled = kwargs.pop("receipting_enabled")

        super().__init__(*args, **kwargs)
        if receipting_enabled:
            message = show_receipting_message(f"checkout_{'yes' if receipt else 'no'}", charity=self.charity)
            self.fields["receipt"].label = message
        else:
            self.fields.pop("receipt", None)


class GivesomeGivecardDonationForm(GivesomeDonationForm):
    suffix = "-gc"
    receipt = BooleanField(disabled=True, help_text="", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["receipt"].label = show_receipting_message("checkout_givecard")


class GivesomeCheckoutPhase(CheckoutPhaseViewMixin, FormView):
    order = None
    project = None

    def get_payment_processor(self):
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        self.service = self.get_payment_processor()
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["shop"] = self.request.shop
        return kwargs

    def get(self, request, *args, **kwargs):
        self.project = ShopProduct.objects.filter(product__pk=self.kwargs.get("pk")).first()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.project = ShopProduct.objects.filter(product__pk=self.kwargs.get("pk")).first()
        return super().post(request, *args, **kwargs)

    def create_order(self, qty):
        """Create an order based on the quantity submitted by the user."""
        basket = Basket(self.request)
        self.basket.clear_all()
        # Qty becomes the total price. So, qty needs to be a decimal proportional to today's exchanged rates.
        converted_qty = convert_to_shop_currency(self.request.user, qty)
        self.basket.add_product(self.project.suppliers.first(), self.request.shop, self.project.product, converted_qty)
        assert basket.shop == self.request.shop
        if not bool(self.basket.get_lines()):
            raise Problem(_("Order doesn't seem to have a project selected."))

        self.basket.orderer = self.request.person
        self.basket.customer = self.request.customer
        self.basket.creator = self.request.user
        self.basket.payment_method = self.service
        if "impersonator_user_id" in self.request.session:
            self.basket.creator = get_user_model().objects.get(pk=self.request.session["impersonator_user_id"])
        self.basket.status = OrderStatus.objects.get_default_initial()

        # Record progress toward project goal:
        order_creator = get_basket_order_creator()
        order = order_creator.create_order(self.basket)
        self.basket.finalize()
        extra = DonationExtra.objects.create(order=order, local_currency_total_value=qty)
        extra.currency = get_preferred_currency(self.request.user)
        extra.save()
        return order

    def get_givecard_funds_sum(self, givecards: GivecardQuerySet):
        return givecards.aggregate(balance_sum=Sum("balance"))["balance_sum"] or 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available, msg = is_project_available(self.project)
        context["allow_donations"] = str(available).lower()
        context["btn_text"] = msg
        context["project"] = self.project
        context["brand"] = ""
        promoter, __ = get_promoter_from_request(self.request)
        user_givecards = get_user_givecards(self.request)
        context["usable_givecards_sum"] = self.get_givecard_funds_sum(
            user_givecards.filter_promoter_usable_givecards(promoter=promoter)
        )
        context["subscription"] = self.project.product.mode == ProductMode.SUBSCRIPTION
        return context

    def form_valid(self, form):
        available, msg = is_project_available(self.project)
        if not available:
            # The project has been fully funded. No need to proceed.
            givecards = get_usable_givecards(self.request)
            return JsonResponse(
                {
                    "funded": None,
                    "available": str(available).lower(),
                    "btnText": msg,
                    "new_current_amt": self.project.product.project_extra.goal_progress_amount,
                    "new_current_amt_preferred_currency": givesome_exchange_currency(
                        self.request.user, self.project.product.project_extra.goal_progress_amount
                    ),
                    "new_current_percent": self.project.product.project_extra.goal_progress_percentage,
                    "givecard_donation_possible": givecards.is_checkout_possible(),
                }
            )

    def get_donation_amount(self):
        suffix = self.form_class.suffix
        return get_donation_amount_value(self.request.POST.get(f"amount{suffix}"))

    def finalize_order(self, order):
        order.save()

        self.checkout_process.complete()  # Inform the checkout process it's completed
        checkout_complete.send(sender=type(self), request=self.request, user=self.request.user, order=self.order)

        # check availability again to be sure
        self.project.refresh_from_db()

    def process(self):
        pass


class GivesomeStripeCheckoutPhase(GivesomeCheckoutPhase):
    form_class = GivesomeStripeDonationForm
    identifier = "checkout"
    template_name = "givesome/modal_checkout.jinja"

    def _is_receipting_enabled(self):
        charity_receipting_enabled = self.project.suppliers.first().givesome_extra.enable_receipting
        project_receipting_enabled = self.project.product.project_extra.enable_receipting
        return charity_receipting_enabled and project_receipting_enabled

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["charity"] = self.project.suppliers.first()
        kwargs["wants_receipt"] = wants_receipt(self.request)
        kwargs["receipting_enabled"] = self._is_receipting_enabled()
        return kwargs

    def get_initial(self):
        return {"receipt": wants_receipt(self.request)}

    def get_payment_processor(self):
        service = PaymentMethod.objects.filter(
            payment_processor__in=StripeMultivendorPaymentProcessor.objects.filter(enabled=True), enabled=True
        ).first()

        if service is None:
            raise Problem(
                _("Please configure the Stripe Multivendor Payment Processor to enable donations by credit card.")
            )
        return service

    def create_stripe_payment_intent(self):
        stripe.api_key = StripeMultivendorPaymentProcessor.objects.filter(enabled=True).first().secret_key
        donation_amount = self.get_donation_amount() * 100  # Stripe takes amount as cents
        stripe_customer = ensure_customer(
            payment_processor=self.get_payment_processor().payment_processor,
            contact=get_person_contact(self.request.user),
        )
        payment_method_id = self.request.POST.get("payment_method_id")
        payment_kwargs = {
            "amount": donation_amount,
            "currency": get_shop(self.request).currency,
            "customer": stripe_customer.stripe_id,
        }
        if "save_for_later" in self.request.POST:
            stripe.PaymentMethod.attach(payment_method_id, customer=stripe_customer.stripe_id)
            payment_kwargs["setup_future_usage"] = "on_session"

        payment_intent = stripe.PaymentIntent.create(**payment_kwargs)
        try:
            stripe.PaymentIntent.confirm(payment_intent.id, payment_method=payment_method_id)
        except stripe.error.CardError as e:
            raise e

        payment_intent_data = {
            "intent": {
                "payment_intent_id": payment_intent.id,
                "secret": payment_intent.client_secret,
                "status": payment_intent.status,
                "amount": donation_amount,
                "supplier": None,
                "target": self.basket.shop.public_name,
                "stripe_customer_id": stripe_customer.stripe_id,
            }
        }

        return payment_intent_data

    def form_valid(self, form):
        already_funded_response = super().form_valid(form)
        if already_funded_response is not None:
            return already_funded_response

        try:
            payment_intents_data = self.create_stripe_payment_intent()
        except stripe.error.CardError as e:
            return JsonResponse({"error": e.user_message}, status=400)

        donation_amount = self.get_donation_amount()
        order = self.create_order(qty=donation_amount)
        order.payment_data = {"stripe_payment_intents": payment_intents_data}
        if self.request.user.is_anonymous:
            order.email = self.request.POST.get("email")
        site_url = self.request.build_absolute_uri()
        order.customer_comment = site_url
        payment_id = payment_intents_data['intent']
        payment_status = stripe.PaymentIntent.retrieve(payment_id['payment_intent_id'],)
        print(payment_status)
        stripe.PaymentIntent.modify(
            payment_intents_data["intent"]["payment_intent_id"],
            description=_("Payment for Givesome donation # {} (to {})".format(order.pk, self.project.product.name)),
        )

        self.finalize_order(order)
        available, msg = is_project_available(self.project)
        return JsonResponse(
            {
                "finalize_url": reverse("shuup:handle_stripe_donation"),
                "home_url": reverse(
                    "shuup:product", kwargs={"pk": self.project.product.pk, "slug": self.project.product.slug}
                ),
                "order_id": order.id,
                "client_secret": order.payment_data["stripe_payment_intents"]["intent"]["secret"],
                "available": str(available).lower(),
                "btnText": msg,
            }
        )

    def get_saved_payment_method(self):
        """See if the user has a payment method already saved"""
        saved_method = stripe.PaymentMethod.list(
            customer=ensure_customer(
                payment_processor=self.service.payment_processor, contact=get_person_contact(self.request.user)
            ).stripe_id,
            type="card",
            limit=1,
        )
        if saved_method:
            return saved_method

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe"] = self.service.payment_processor.publishable_key
        context["payment_method_id"] = ""
        context["last4"] = ""
        saved_payment_method = self.get_saved_payment_method()
        if saved_payment_method is not None:
            context["payment_method_id"] = saved_payment_method["data"][0]["id"]
            context["brand"] = saved_payment_method["data"][0]["card"]["brand"].title()
            context["last4"] = saved_payment_method["data"][0]["card"]["last4"]

        context["receipting_enabled"] = self._is_receipting_enabled()
        is_eligible = user_is_eligible(self.request.user)
        context["can_request_receipt"] = is_eligible
        if not is_eligible:
            context["next_stop"] = reverse("shuup:start-receipting")
        context["wants_receipt"] = wants_receipt(self.request)
        return context


class GivesomeGivecardCheckoutPhase(GivesomeCheckoutPhase):
    form_class = GivesomeGivecardDonationForm
    identifier = "givecard-checkout"
    template_name = "givesome/modal_checkout_givecard.jinja"

    def get_initial(self):
        # Note: Givecard donations are not eligible for receipting.
        return {"receipt": False}

    def get_payment_processor(self):
        service = PaymentMethod.objects.filter(
            payment_processor__in=GivecardPaymentProcessor.objects.filter(enabled=True), enabled=True
        ).first()

        if service is None:
            raise Problem(_("Please configure the Givecard Payment Processor to enable donations by Givecard."))
        return service

    def get_givecard_funds_sum(self, givecards: GivecardQuerySet):
        return givecards.aggregate(balance_sum=Sum("balance"))["balance_sum"] or 0

    def form_valid(self, form):
        already_funded_response = super().form_valid(form)
        if already_funded_response is not None:
            return already_funded_response

        donation_amount = self.get_donation_amount()

        usable_givecards = get_usable_givecards(self.request)
        if self.request.user.is_anonymous:
            usable_givecards = usable_givecards.filter(user=None)
        usable_wallet_balance = self.get_givecard_funds_sum(usable_givecards)

        if usable_wallet_balance < donation_amount:
            # User didn't have enough funds, next we need to tell them why.
            # First get the total balance from cached wallet
            total_wallet_balance = self.get_givecard_funds_sum(get_user_givecards(self.request).usable())
            if self.request.user.is_anonymous:
                # Refresh cached wallet from db to check if any Givecard funds have been used/claimed by other users.
                bump_wallet_cache(self.request)
                # Get Givecard sum for refreshed wallet
                new_wallet_balance = self.get_givecard_funds_sum(get_usable_givecards(self.request))
                # User had funds in their wallet at some point to initiate Givecard checkout,
                # but after refreshing the funds from database, they are no longer available.
                # This means they must have been spent/claimed by another user.
                if total_wallet_balance > new_wallet_balance:
                    raise Problem(
                        _(
                            "Not enough Givecard funds. "
                            "Some of your Givecard funds may have been already used by another user. "
                            "All invalid Givecards have been cleared from your wallet. "
                            "Please refresh this page."
                        )
                    )
            # User has enough Givecard funds, but they are not usable on this page
            if total_wallet_balance > usable_wallet_balance:
                raise Problem(
                    _("You have enough Givecard funds, but these funds can only be used on a specific brand page.")
                )
            # User does not have enough funds
            raise Problem(_("Oops. First donate the remainder of your PIN dollars before using your credit card."))

        order = self.create_order(qty=donation_amount)
        self.finalize_order(order)

        available, msg = is_project_available(self.project)
        return JsonResponse(
            {
                "finalize_url": reverse("shuup:handle_givecard_donation"),
                "home_url": reverse(
                    "shuup:product", kwargs={"pk": self.project.product.pk, "slug": self.project.product.slug}
                ),
                "order_id": order.id,
                "available": str(available).lower(),
                "btnText": msg,
            }
        )


def is_project_available(project):
    """Determine if the current project is eligible for donations"""
    available = False
    message = None
    if project.product.project_extra.fully_funded_date is not None:
        message = _("THANK YOU FOR YOUR GENEROSITY, THIS PROJECT HAS BEEN FULLY FUNDED")
    elif not project.purchasable and project.product.mode != ProductMode.SUBSCRIPTION:
        message = _("Check back later to make a donation!")
    elif project.visibility not in [ShopProductVisibility.ALWAYS_VISIBLE, ShopProductVisibility.ONLY_VISIBLE_WHEN_PROMOTED]:
        message = _("The donation period for this project has been concluded.")
    else:
        available = True

    return available, message

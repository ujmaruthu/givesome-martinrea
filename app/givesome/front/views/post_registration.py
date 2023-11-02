# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import is_safe_url
from django.utils.timezone import now
from shuup.admin.supplier_provider import get_supplier
from shuup.core.models import Order
from shuup.front.utils.user import is_admin_user
from shuup_firebase_auth.views.auth import FirebaseAuthView
from shuup_firebase_auth.views.register import FirebaseRegisterView

from givesome.front.receipting_checkout_state import (
    ReceiptingCheckoutState,
    set_receipting_session_info,
    user_is_eligible,
    wants_receipt,
    within_time,
)


class PostRegistrationView(FirebaseRegisterView):
    """When creating an account directly after making a donation, try to remember the donation just made."""

    def get(self, request, *args, **kwargs):
        # Set 10-minute limit for remembering the recent donation's id.
        request.session.set_expiry(600)
        request.session["order_id"] = self.kwargs["order_id"]
        return super(PostRegistrationView, self).get(request, *args, **kwargs)


class GivesomeFirebaseAuthView(FirebaseAuthView):
    def dispatch(self, request, *args, **kwargs):
        self.wants_receipt = wants_receipt(request) and within_time(request)
        if self.wants_receipt and not self.request.user.is_anonymous:
            # Continue to the next step in the receipting process - already logged in.
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.wants_receipt:
            # The user has started the receipting journey within the last few minutes, so special template needed.
            return ["givesome/receipting_login.jinja"]

        return super().get_template_names()

    def get_success_url(self, *args, **kwargs):
        if self.wants_receipt:
            # The user wants a receipt and has successfully authenticated. Figure out where they need to go next.
            set_receipting_session_info(self.request)
            is_eligible = user_is_eligible(self.request.user)
            return ReceiptingCheckoutState(
                self.request.session["point_of_origin"], state="login-or-register", eligible=is_eligible
            ).get_next_url()

        if is_admin_user(self.request) or get_supplier(self.request):
            return reverse("shuup_admin:dashboard")

        url = self.request.POST.get(REDIRECT_FIELD_NAME)
        if url and is_safe_url(url, self.request.get_host()):
            return url
        return "/"

    def register(self, form):
        """If registering immediately after making an anonymous donation, recall the donation.
        Or, if the user is in the receipting process, remember session data to keep the process going.
        """
        order = None
        if "order_id" in self.request.session:
            order = Order.objects.filter(id=self.request.session["order_id"]).first()
        point_of_origin = None
        if wants_receipt(self.request) and "point_of_origin" in self.request.session:
            point_of_origin = self.request.session["point_of_origin"]

        # Anonymous session data is about to be thrown away.
        auth_user = super(GivesomeFirebaseAuthView, self).register(form)

        if order is not None:
            order.customer = auth_user.contact
            order.save()

        if point_of_origin:
            self.request.session["requesting_receipt"] = True
            self.request.session["receipt_timecheck"] = now()
            self.request.session["point_of_origin"] = point_of_origin
            self.request.session["newcomer"] = True
        return auth_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.wants_receipt:
            context["changed_mind"] = reverse("shuup:no-receipting")
        return context

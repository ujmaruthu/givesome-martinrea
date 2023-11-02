# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from shuup_firebase_auth.views.customer_information import CustomerEditView

from givesome.front.receipting_checkout_state import (
    ReceiptingCheckoutState,
    set_receipting_session_info,
    user_is_eligible,
    wants_receipt,
    within_time,
)


class GivesomeCustomerEditView(CustomerEditView):
    def get_success_url(self):
        if wants_receipt(self.request) and self.request.session.get("point_of_origin"):
            is_eligible = user_is_eligible(self.request.user)
            return HttpResponseRedirect(
                ReceiptingCheckoutState(
                    self.request.session["point_of_origin"], state="profile", eligible=is_eligible
                ).get_next_url()
            )
        else:
            return redirect("shuup_firebase_auth:customer_edit")

    def form_valid(self, form):
        # Don't call super as the parent implementation doesn't call `get_success_url`
        form.save()
        messages.success(self.request, _("Account information saved successfully."))

        set_receipting_session_info(self.request)
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        receipt = wants_receipt(self.request) and within_time(self.request)
        # Show the following only if the user wants a receipt and is under 2 minutes from the last receipting action.
        if receipt:
            context["wants_receipt"] = receipt
            context["changed_mind"] = reverse("shuup:no-receipting")
        return context

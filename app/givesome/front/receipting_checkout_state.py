# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from datetime import timedelta
from typing import Dict

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from shuup.core.models import get_person_contact


class ReceiptingCheckoutState:
    """Shepherd the user through the process of qualifying for a receipt and bring them back safely to their
    checkout page, with the appropriate defaults selected (based on their choices along the way).
    """

    states = {
        "initial": {"complete": "complete", "next": "login-or-register", "previous": ""},
        "login-or-register": {"complete": "complete", "next": "profile", "previous": "initial"},
        "profile": {"complete": "initial", "next": "initial", "previous": "initial"},
        "complete": {"complete": "initial", "next": "initial", "previous": ""},
    }

    def __init__(self, initial_url: str, state="initial", want_receipt=True, eligible=True):
        self.urls = {
            "initial": initial_url,
            "login-or-register": reverse("shuup:givesome-auth"),
            "profile": reverse("shuup:customer_edit"),
            "complete": initial_url,
        }

        self.want_receipt: bool = want_receipt
        self.eligible = eligible
        # Current state is a collection of choices: complete, next, or previous?
        self.current_state: Dict[str, str] = self.states[state]

    @property
    def next_state(self) -> str:
        """Determine which state the user should be in next based on current choices. Return value is a key to use
        in the next instance's `states` variable.
        """
        if not self.want_receipt and not self.eligible:
            # The user does not want a receipt is isn't eligible anyway. Abort.
            next_state = self.current_state["previous"]
            return next_state if next_state else self.states[self.current_state["complete"]]["next"]

        elif self.want_receipt and not self.eligible:
            # The wants a receipt and isn't eligible. Proceed to the next step.
            return self.current_state["next"]

        else:
            # The user is eligible, and wanting a receipt or not won't change the page where they end up.
            return self.current_state["complete"]

    def get_next_url(self) -> str:
        return self.urls[self.next_state]


def user_is_eligible(user):
    """Determine if the user is currently eligible to request a receipt."""
    if user.is_anonymous:
        # Must be logged in
        return False
    else:
        person_contact = get_person_contact(user)
        if not person_contact.first_name or not person_contact.last_name:
            # Incomplete profile
            return False

        billing_address = person_contact.default_billing_address
        if not billing_address:
            # Incomplete profile
            return False

        if (
            not billing_address.street
            or not billing_address.city
            or not billing_address.region
            or not billing_address.country
        ):
            # Incomplete profile
            return False

    return True


def within_time(request) -> bool:
    """Determine if the user is under 2 minutes from the last receipting timestamp. If not, forget about the process."""
    timestamp = request.session.get("receipt_timecheck")
    # Brand new users (i.e. anonymous and users who have just registered for the first time) get 4 minutes.
    limit = 4 if request.user.is_anonymous or request.session.get("newcomer") else 2
    still_time_remaining = timestamp and timestamp + timedelta(minutes=limit) >= timezone.now()
    if not still_time_remaining:
        request.session.pop("requesting_receipt", None)
        request.session.pop("receipt_timecheck", None)
        request.session.pop("point_of_origin", None)
        request.session.pop("newcomer", None)
    return still_time_remaining


def wants_receipt(request):
    """Deterimine if the user wants a receipt. 3 possibilities: yes, no, and undetermined (None)."""
    wishes = request.session.get("requesting_receipt")
    return wishes if wishes is not None else True


def set_receipting_session_info(request, want_receipt=True):
    """Set information in the session to guide the user through the process of qualifying for a receipt."""

    if want_receipt and request.GET.get("origin"):
        request.session["requesting_receipt"] = want_receipt
        request.session["receipt_timecheck"] = timezone.now()
        if "point_of_origin" not in request.session:
            origin = "/p/" + request.GET.get("origin")
            if "?type" in origin and request.GET.get("id"):
                # The querystring params confused Django a bit. Reconstruct the original url:
                origin = f"{origin}&id={request.GET.get('id')}"
            request.session["point_of_origin"] = origin
    elif not want_receipt:
        request.session["requesting_receipt"] = want_receipt

    return request


def initial_sign_up_for_receipt(request):
    if request.method == "GET":
        request = set_receipting_session_info(request)
        return HttpResponseRedirect(
            ReceiptingCheckoutState(request.session["point_of_origin"], state="initial", eligible=False).get_next_url()
        )


def changed_my_mind_about_receipt(request):
    """The donor changed their minds. Go back to the point of origin with the correct information in the session."""
    point_of_origin = request.session["point_of_origin"]
    set_receipting_session_info(request, want_receipt=False)
    next_url = ReceiptingCheckoutState(point_of_origin, state="initial").get_next_url()
    return HttpResponseRedirect(next_url)

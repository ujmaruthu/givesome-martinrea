# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from datetime import datetime, timedelta

import mock
import pytest
import pytz
from django.urls import reverse
from django.utils import timezone
from shuup.testing import factories
from shuup.testing.utils import apply_request_middleware

from givesome.front.receipting_checkout_state import ReceiptingCheckoutState, set_receipting_session_info, within_time


def test_receipting_checkout_state_initial_to_complete():
    rcs = ReceiptingCheckoutState("foo/", state="initial", want_receipt=True, eligible=True)

    assert rcs.next_state == "complete"
    assert rcs.get_next_url() == "foo/"


def test_receipting_checkout_state_initial_to_next():
    rcs = ReceiptingCheckoutState("foo/", state="initial", want_receipt=True, eligible=False)

    assert rcs.next_state == "login-or-register"
    assert rcs.get_next_url() == reverse("shuup:givesome-auth")


def test_receipting_checkout_state_login_to_profile():
    rcs = ReceiptingCheckoutState("foo/", state="login-or-register", want_receipt=True, eligible=False)

    assert rcs.next_state == "profile"
    assert rcs.get_next_url() == reverse("shuup:customer_edit")


def test_receipting_checkout_state_changed_mind_login_to_initial():
    rcs = ReceiptingCheckoutState("foo/", state="login-or-register", want_receipt=False, eligible=False)

    assert rcs.next_state == "initial"
    assert rcs.get_next_url() == "foo/"


def test_receipting_checkout_state_profile_to_initial():
    rcs = ReceiptingCheckoutState("foo/", state="profile", want_receipt=True, eligible=True)

    assert rcs.next_state == "initial"
    assert rcs.get_next_url() == "foo/"


def test_receipting_checkout_state_changed_mind_profile_to_initial():
    rcs = ReceiptingCheckoutState("foo/", state="initial", want_receipt=False, eligible=False)

    assert rcs.next_state == "initial"
    assert rcs.get_next_url() == "foo/"


@pytest.mark.django_db
def test_within_time_is_accurate_for_the_types_of_users(rf):
    fake_timestamp = timezone.make_aware(datetime(2021, 11, 1), timezone=pytz.utc)
    shop = factories.get_default_shop()
    # Anonymous user gets 4 minutes
    request = apply_request_middleware(rf.get("/?origin=asdf"), shop=shop)

    with mock.patch.object(timezone, "now", return_value=fake_timestamp):
        set_receipting_session_info(request)
    with mock.patch.object(timezone, "now", return_value=fake_timestamp + timedelta(minutes=3)):
        assert within_time(request)
    with mock.patch.object(timezone, "now", return_value=fake_timestamp + timedelta(minutes=4, seconds=1)):
        assert not within_time(request)

    # Freshly registered user gets 4 minutes
    user = factories.create_random_user()
    request = apply_request_middleware(rf.get("/?origin=asdf"), shop=shop, user=user)
    with mock.patch.object(timezone, "now", return_value=fake_timestamp):
        set_receipting_session_info(request)
        request.session["newcomer"] = True
    with mock.patch.object(timezone, "now", return_value=fake_timestamp + timedelta(minutes=3)):
        assert within_time(request)
    with mock.patch.object(timezone, "now", return_value=fake_timestamp + timedelta(minutes=4, seconds=1)):
        assert not within_time(request)

    # Everybody else gets 2 minutes
    request = apply_request_middleware(rf.get("/?origin=asdf"), shop=shop, user=user)
    with mock.patch.object(timezone, "now", return_value=fake_timestamp):
        set_receipting_session_info(request)
    with mock.patch.object(timezone, "now", return_value=fake_timestamp + timedelta(minutes=1)):
        assert within_time(request)
    with mock.patch.object(timezone, "now", return_value=fake_timestamp + timedelta(minutes=2, seconds=1)):
        assert not within_time(request)

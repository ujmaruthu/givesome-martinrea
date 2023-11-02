# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from shuup.simple_cms.views import PageView

from givesome.front.views import CharityRegistrationView, GivesomeSupplierView, PartnerRegistrationView
from givesome.front.views.homepage import GivesomeIndexView
from givesome.front.views.post_registration import GivesomeFirebaseAuthView, PostRegistrationView
from givesome.front.views.profile import ProfileView
from givesome.front.views.competition import GivesomeCompetitionView

from .checkout import GivesomeGivecardCheckoutPhase, GivesomeStripeCheckoutPhase
from .receipting_checkout_state import changed_my_mind_about_receipt, initial_sign_up_for_receipt
from .views import SetTimezoneView
from .views.checkout import GivesomeGivecardPaymentView, GivesomeStripePaymentView
from .views.vendor_information import VendorInformationDetailView

urlpatterns = [
    url(r"^$", GivesomeIndexView.as_view(), name="index"),
    url(r"^set-timezone/", SetTimezoneView.as_view(), name="set_timezone"),
    url(r"^v/register/$", CharityRegistrationView.as_view(), name="charity_registration"),
    url(r"^b/register/$", PartnerRegistrationView.as_view(), name="partner_registration"),
    url(r"^profile/$", login_required(ProfileView.as_view()), name="profile"),
    url(r"^vendor_information/(?P<pk>\d+)/$", VendorInformationDetailView.as_view(), name="vendor_information"),
    url(r"^stripe/handle-stripe-donation/$", GivesomeStripePaymentView.as_view(), name="handle_stripe_donation"),
    url(r"^handle_givecard_donation/$", GivesomeGivecardPaymentView.as_view(), name="handle_givecard_donation"),
    url(r"^donation_form/(?P<pk>\d+)/$", GivesomeStripeCheckoutPhase.as_view(), name="donation_form"),
    url(
        r"^givecard_donation_form/(?P<pk>\d+)/$", GivesomeGivecardCheckoutPhase.as_view(), name="givecard_donation_form"
    ),
    url(r"^receipting/$", initial_sign_up_for_receipt, name="start-receipting"),
    url(r"^receipting-changed-mind/$", changed_my_mind_about_receipt, name="no-receipting"),
    url(r"^post-register/(?P<order_id>\d+)/$", PostRegistrationView.as_view(), name="register-after-donation"),
    url(r"^givesome-auth/", GivesomeFirebaseAuthView.as_view(), name="givesome-auth"),
    url(r"^competition/(?P<slug>[^/]+)/$", GivesomeCompetitionView.as_view(), name="competition"),
    url(r"^cms/(?P<url>.*)/$", PageView.as_view(), name="cms_page"),  # Override CMS page URL
    url(r"^(?P<slug>[^/]+)/$", GivesomeSupplierView.as_view(), name="supplier"),  # Vendor URL with only slug
]

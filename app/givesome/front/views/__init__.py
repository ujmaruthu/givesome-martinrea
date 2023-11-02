# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from givesome.front.views.checkout import CheckoutViewWithLoginAndRegisterVertical
from givesome.front.views.profile import (
    OffPlatformCreateView,
    OffPlatformDeleteView,
    OffPlatformListView,
    OffPlatformUpdateView,
    ProfileView,
)
from givesome.front.views.supplier import GivesomeBrandedList, GivesomeCharityList, GivesomeSupplierView
from givesome.front.views.timezone import SetTimezoneView
from givesome.front.views.vendor_registration import CharityRegistrationView, PartnerRegistrationView

__all__ = [
    "CheckoutViewWithLoginAndRegisterVertical",
    "ProfileView",
    "GivesomeBrandedList",
    "GivesomeCharityList",
    "GivesomeSupplierView",
    "SetTimezoneView",
    "CharityRegistrationView",
    "PartnerRegistrationView",
    "OffPlatformCreateView",
    "OffPlatformUpdateView",
    "OffPlatformListView",
    "OffPlatformDeleteView",
]

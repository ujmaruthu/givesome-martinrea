# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from shuup_multivendor.views import VendorRegistrationView

from givesome.front.forms.vendor_registration import CharityRegistrationForm, PartnerRegistrationForm


class CharityRegistrationView(VendorRegistrationView):
    def get_form_class(self):
        return CharityRegistrationForm


class PartnerRegistrationView(VendorRegistrationView):
    def get_form_class(self):
        return PartnerRegistrationForm

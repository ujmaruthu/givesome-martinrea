# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.forms import Textarea
from shuup.admin.forms import ShuupAdminForm

from givesome.models import ReceiptingMessages

_textarea = Textarea(attrs={"rows": 3})


class ReceiptingMessagesForm(ShuupAdminForm):
    class Meta:
        model = ReceiptingMessages
        fields = (
            "welcome",
            "project_card",
            "charity_page",
            "project_page",
            "checkout_no",
            "checkout_yes",
            "checkout_warn",
            "checkout_givecard",
            "portfolio",
            "sign_in_header",
            "sign_in_step_1",
            "sign_in_step_2",
            "sign_in_step_3",
        )
        widgets = {
            "welcome": _textarea,
            "project_card": _textarea,
            "charity_page": _textarea,
            "project_page": _textarea,
            "checkout_no": _textarea,
            "checkout_yes": _textarea,
            "checkout_warn": _textarea,
            "checkout_givecard": _textarea,
            "portfolio": _textarea,
            "sign_in_header": _textarea,
            "sign_in_step_1": _textarea,
            "sign_in_step_2": _textarea,
            "sign_in_step_3": _textarea,
        }

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shuup.admin.toolbar import URLActionButton


class OrderPaymentLinkAction(URLActionButton):
    def __init__(self, object, **kwargs):
        kwargs["url"] = reverse("shuup:order_process_payment", kwargs={"pk": object.pk, "key": object.key})
        kwargs["icon"] = "fa fa-credit-card-alt"
        kwargs["text"] = _("Go to payment page")
        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(object):
        return object.can_create_payment() and not object.is_deferred()

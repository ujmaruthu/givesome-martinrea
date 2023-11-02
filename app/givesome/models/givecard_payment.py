# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import PaymentProcessor, ServiceChoice


class GivecardPaymentProcessor(PaymentProcessor):
    class Meta:
        verbose_name = _("Givecard processor")
        verbose_name_plural = _("Givecard processors")

    def get_service_choices(self):
        return [ServiceChoice("givecard", _("Givecard checkout"))]

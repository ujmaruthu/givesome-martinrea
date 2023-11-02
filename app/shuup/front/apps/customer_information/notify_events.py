# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.notify.base import Event, Variable
from shuup.notify.typology import Email, Model


class CompanyAccountCreated(Event):
    identifier = "company_account_created"

    contact = Variable("CompanyContact", type=Model("shuup.CompanyContact"))
    customer_email = Variable(_("Customer Email"), type=Email)

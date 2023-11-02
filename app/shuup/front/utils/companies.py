# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from shuup import configuration
from shuup.core.utils import tax_numbers
from shuup.front.setting_keys import SHUUP_ALLOW_COMPANY_REGISTRATION, SHUUP_COMPANY_REGISTRATION_REQUIRES_APPROVAL


def allow_company_registration(shop):
    return configuration.get(shop, SHUUP_ALLOW_COMPANY_REGISTRATION, default=False)


def company_registration_requires_approval(shop):
    return configuration.get(shop, SHUUP_COMPANY_REGISTRATION_REQUIRES_APPROVAL, default=False)


def validate_tax_number(shop):
    return configuration.get(shop, "validate_tax_number", default=False)


class TaxNumberCleanMixin(object):
    company_name_field = "name"

    def clean_tax_number(self):
        tax_number = self.cleaned_data["tax_number"].strip()
        if self.request and validate_tax_number(self.request.shop) and tax_number:
            if tax_numbers.validate(tax_number) != "vat":
                raise ValidationError(_("Tax number is not valid."), code="not_valid_tax_number")

        return tax_number

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class VendorExtraType(Enum):
    CHARITY = 1
    BRANDED_VENDOR = 2

    class Labels:
        CHARITY = _("Charity")
        BRANDED_VENDOR = _("Branded vendor")


class GivecardDonateRestrictionType(Enum):
    DISABLED = 1
    SUPPLIER = 2
    OFFICE = 3

    class Labels:
        DISABLED = _("Disabled")
        SUPPLIER = _("Brand Vendor")
        OFFICE = _("Office")


class GivecardBatchExpiryType(Enum):
    DISABLED = 1
    AUTOMATIC = 2
    MANUAL = 3

    class Labels:
        DISABLED = _("Disabled")
        AUTOMATIC = _("Automatic")
        MANUAL = _("Manual")


class DonationType(Enum):
    ONE_TIME = 0
    SUBSCRIPTION = 1

    class Labels:
        ONE_TIME = _("One-Time")
        SUBSCRIPTION = _("Subscription")


class GivesomeDonationType(Enum):
    PURSE_MANUAL = 0  # Manual:       Givesome Purse
    PURSE_AUTOMATIC = 1  # Automatic: Givesome Purse
    OFFICE_PRIMARY = 2  # Automatic:  Project is Office's primary project
    BRAND_PRIMARY = 3  # Automatic:   Project is Brand Vendor's primary project
    OFFICE_PROMOTED = 4  # Automatic: Project is promoted by Office
    BRAND_PROMOTED = 5  # Automatic:  Project is promoted by Supplier

    class Labels:
        PURSE_MANUAL = _("Purse Manual")
        PURSE_AUTOMATIC = _("Purse Automatic")
        OFFICE_PRIMARY = _("Office Primary Project")
        BRAND_PRIMARY = _("Brand Primary Project")
        OFFICE_PROMOTED = _("Office Promoted Project")
        BRAND_PROMOTED = _("Brand Promoted Project")

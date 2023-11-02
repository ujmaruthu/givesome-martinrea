# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumIntegerField

from givesome.enums import VendorExtraType


class VendorExtra(models.Model):

    vendor_type = EnumIntegerField(
        VendorExtraType,
        default=VendorExtraType.CHARITY,
        verbose_name=_("vendor type"),
        help_text=_(
            "Charities may sign up as charities in order to create charity projects. They "
            "may pay to upgrade to Branded Vendor status if they wish, which will enable "
            "them to feature their projects on their Branded Vendor Page."
        ),
    )
    allow_brand_page = models.BooleanField(default=True)
    allow_purse = models.BooleanField(default=False)
    enable_receipting = models.BooleanField(default=False)
    vendor = models.OneToOneField(
        "shuup.Supplier",
        related_name="givesome_extra",
        on_delete=models.CASCADE,
        help_text=_("The vendor described by this extra information."),
    )
    website_url = models.CharField(
        null=True,
        blank=True,
        max_length=128,
        verbose_name=_("URL"),
        help_text=_("Enter the URL of the vendor's website."),
    )
    color = models.CharField(
        null=True,
        blank=True,
        max_length=7,
        verbose_name=_("Hex colour code"),
        help_text=_("Enter the hex code of the organization's main colour."),
    )
    primary_project = models.ForeignKey(
        "shuup.ShopProduct",
        related_name="primary_suppliers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Primary project"),
        help_text=_("Selected project will be prioritized when automatically reallocating expiring Givecard funds."),
    )
    ordering = models.IntegerField(default=0)
    sponsored_by = models.ForeignKey(
        "shuup.Supplier",
        related_name="sponsored_charities",
        verbose_name=_("Sponsored by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    sponsor_link = models.CharField(max_length=128, null=True, blank=True)
    registration_number = models.CharField(max_length=50, null=True, blank=True)
    show_promoted = models.BooleanField(
        default=True,
        verbose_name=_("Show promoted projects"),
        help_text=_("Show promoted projects"),
    )
    display_type = models.IntegerField(default=0)

    @property
    def pretty_website_url(self):
        """Remove any http and www from the link"""
        if self.website_url:
            url = re.compile(r"https?://(www\.)?")
            return url.sub("", self.website_url).strip().strip("/")
        return ""

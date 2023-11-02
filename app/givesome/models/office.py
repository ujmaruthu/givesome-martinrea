# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from shuup.core.models import ShuupModel


class GivesomeOffice(MPTTModel, ShuupModel):
    """Sub-vendor for companies with branded page"""

    supplier = models.ForeignKey("shuup.Supplier", on_delete=models.CASCADE, related_name="offices")
    name = models.CharField(max_length=64, verbose_name=_("name"))
    ordering = models.IntegerField(default=0, verbose_name=_("ordering"))
    disabled = models.BooleanField(
        default=False,
        help_text=_(
            "Disable this office. This office will not be show in the front for customers anymore. "
            "All children offices are affected as well. "
            "Any related Givecard restrictions will be left unaffected, which means that if any Batches are "
            "restricted to this Office or any child offices, it will be impossible to use any of those Givecards."
        ),
    )
    primary_project = models.ForeignKey(
        "shuup.ShopProduct",
        related_name="primary_offices",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Primary project"),
        help_text=_("Selected project will be prioritized when automatically reallocating expiring Givecard funds."),
    )
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent office"),
        on_delete=models.SET_NULL,
        help_text=_("If your office is a sub-office of another office, you can link them here."),
    )

    class Meta:
        ordering = ("supplier", "level", "ordering")

    def __str__(self):
        name = self.name
        for ancestor in self.get_ancestors(ascending=True):  # Immediate parents first
            name = f"{name} > {ancestor.name}"
        return f"{name} > {self.supplier.name}"


class SupplierOfficeTerm(models.Model):
    supplier = models.ForeignKey(
        "shuup.Supplier",
        related_name="office_terms",
        on_delete=models.CASCADE,
    )
    level = models.PositiveIntegerField(default=0)
    name = models.CharField(
        max_length=32,
        verbose_name=_("Office term"),
        help_text=_("Enter a term you want to use for your offices/chapters/locations."),
    )

    class Meta:
        unique_together = ("supplier", "level")
        ordering = ("supplier", "level")

    def __str__(self):
        return self.name

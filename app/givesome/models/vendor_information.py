# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from shuup.core import cache
from shuup.core.fields import InternalIdentifierField
from shuup.core.signals import context_cache_item_bumped


class VendorInformation(TranslatableModel):
    class Meta:
        verbose_name_plural = "Vendor Information"

    identifier = InternalIdentifierField(unique=False, editable=False)
    translations = TranslatedFields(
        title=models.CharField(max_length=64),
        page=models.TextField(
            verbose_name=_("Vendor and Charity Information"),
            help_text=_("Describe any information that vendors and charities should know."),
        ),
    )

    def __str__(self):
        return force_text(self.safe_translation_getter("title"))

    @staticmethod
    def bump_cache():
        cache.bump_version("vendor_information")
        qs = VendorInformation.objects.all()
        context_cache_item_bumped.send(getattr(qs, "__class__", qs), item=qs)

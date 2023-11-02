# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.db.models import Count, Q
from django.forms import Select
from django.utils.translation import ugettext_lazy as _
from shuup.admin.forms import ShuupAdminFormNoTranslation
from shuup.core.models import Supplier

from givesome.enums import VendorExtraType
from givesome.models import GivesomeCompetition, GivesomeGroup


class GivesomeCompetitionForm(ShuupAdminFormNoTranslation):
    class Meta:
        model = GivesomeCompetition
        fields = (
            "competition_runner",
            "slug",
            "competition_key",
            "start_date",
            "end_date",
            "competitors",
            "active",
        )

    def __init__(self, **kwargs):
        """Restrict supplier choices to brand vendors"""
        self.request = kwargs.pop("request", None)
        super().__init__(**kwargs)

    def save(self, commit=False):
        return super().save(commit=True)

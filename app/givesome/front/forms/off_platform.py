# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.forms import HiddenInput, ModelForm

from givesome.models import OffPlatformDonation, VolunteerHours


class VolunteerHoursForm(ModelForm):
    class Meta:
        model = VolunteerHours
        fields = "__all__"
        widgets = {"donor": HiddenInput()}


class OffPlatformDonationForm(ModelForm):
    class Meta:
        model = OffPlatformDonation
        fields = "__all__"
        widgets = {"donor": HiddenInput()}

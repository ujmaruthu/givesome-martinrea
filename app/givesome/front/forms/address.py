# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import MutableAddress
from shuup_firebase_auth.views.customer_information import AddressForm


class GivesomeAddressForm(AddressForm):
    class Meta:
        model = MutableAddress
        fields = (
            "name",
            "street",
            "postal_code",
            "city",
            "region",
            "region_code",
            "country",
        )

    def __init__(self, **kwargs):
        # Do not use settings.SHUUP_ADDRESS_FIELD_PROPERTIES
        super(forms.ModelForm, self).__init__(**kwargs)

        if not kwargs.get("instance"):
            # Set default country
            self.fields["country"].initial = settings.SHUUP_ADDRESS_HOME_COUNTRY

        if kwargs["prefix"] == "billing":
            # Additional required fields
            self.fields["region"].required = True
            self.fields["postal_code"].required = True

            # Custom labels
            self.fields["postal_code"].label = _("Postal/Zip code")
            self.fields["region"].label = _("Province/State")
            # self.fields["region_code"].label = _("Province/State Abbreviation.")
        else:
            # No shipping information should be required.
            for field_key in self.fields:
                self.fields[field_key].required = False

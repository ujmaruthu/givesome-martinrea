# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms

from shuup.apps.provides import get_provide_objects


class CompanyAgreementForm(forms.Form):
    def __init__(self, **kwargs):
        self.shop = kwargs.pop("shop")
        self.request = kwargs.pop("request")
        super(CompanyAgreementForm, self).__init__(**kwargs)
        for provider_cls in get_provide_objects("front_registration_field_provider"):
            provider = provider_cls()
            for definition in provider.get_fields(request=self.request):
                self.fields[definition.name] = definition.field

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django import forms
from django.utils.translation import ugettext_lazy as _
from shuup.front.providers import FormFieldDefinition, FormFieldProvider


class GivesomeRegistrationFormProvider(FormFieldProvider):
    error_message = _("Please supply the website address for your organization.")

    def get_fields(self, **kwargs):
        fields = []
        url_field = forms.CharField(
            label=_("Website"),
            error_messages=dict(required=self.error_message),
            help_text=_("The website address for the organization."),
        )
        definition = FormFieldDefinition(name="website_url", field=url_field)
        fields.append(definition)
        return fields

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django import forms

from shuup.core.models import SMTPAccount


class SMTPAccountBaseForm(forms.ModelForm):
    class Meta:
        model = SMTPAccount
        fields = (
            "name",
            "default_from_email",
            "username",
            "password",
            "host",
            "port",
            "protocol",
            "shop",
            "timeout",
            "ssl_certfile",
            "ssl_keyfile",
            "default_account",
        )
        widgets = {
            "password": forms.PasswordInput(render_value=True),
            "protocol": forms.Select(),
        }

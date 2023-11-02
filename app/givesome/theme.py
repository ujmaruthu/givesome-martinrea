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
from shuup_definite_theme.theme import ShuupDefiniteTheme


class GivesomeTheme(ShuupDefiniteTheme):
    identifier = "givesome"
    name = _("Givesome Theme")
    author = "Shuup Team"

    guide_template = "givesome/guide.jinja"

    template_dir = "givesome/"
    default_template_dir = "shuup_definite_theme/"

    stylesheets = []

    fields = [
        ("product_new_days", forms.IntegerField(required=False, initial=14, label=_("Consider product new for days"))),
        (
            "allow_company_linkage",
            forms.BooleanField(required=False, initial=False, label=_("Allow Linking Accounts to Company")),
        ),
    ]

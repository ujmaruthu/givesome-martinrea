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

from shuup.core.models import Product
from shuup.xtheme import TemplatedPlugin


class HighlightTestPlugin(TemplatedPlugin):
    identifier = "shuup_test_theme.product_highlight"
    name = _("Shuup Test Theme Product Highlights")
    template_name = "shuup_testing/highlight_plugin.jinja"
    fields = [
        ("title", forms.CharField(required=False, initial="")),
        ("count", forms.IntegerField(min_value=1, initial=8)),
    ]

    def get_context_data(self, context):
        count = self.config.get("count", 8)

        return {
            "request": context["request"],
            "title": self.config.get("title"),
            "products": Product.objects.all()[:count],
        }

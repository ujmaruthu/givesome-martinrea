# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.xtheme.layout import Layout


class ProductLayout(Layout):
    identifier = "xtheme-product-layout"

    def get_help_text(self, context):
        product = context.get("product")
        if not product:
            return ""
        return _("Content in this placeholder is shown for %(product_name)s only." % {"product_name": product.name})

    def is_valid_context(self, context):
        return bool(context.get("product"))

    def get_layout_data_suffix(self, context):
        return "%s-%s" % (self.identifier, context["product"].pk)

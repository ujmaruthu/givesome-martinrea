# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import Supplier
from shuup.xtheme import TemplatedPlugin

# TODO: Change this plugin so that the user can pick up 12 of their preferred vendors.
from givesome.enums import VendorExtraType


class HomepageVendorsPlugin(TemplatedPlugin):
    identifier = "homepage_vendors"
    name = _("Homepage Vendors")
    template_name = "givesome/plugins/homepage_vendors.jinja"
    fields = [
        (
            "type",
            forms.ChoiceField(
                label=_("Type of vendor to show"),
                choices=VendorExtraType.choices(),
                initial=VendorExtraType.BRANDED_VENDOR,
            ),
        ),
        ("count", forms.IntegerField(label=_("Count"), min_value=1, initial=12)),
    ]

    def get_context_data(self, context):
        type = self.config.get("type", VendorExtraType.BRANDED_VENDOR)
        count = self.config.get("count", 4)

        vendors = (
            Supplier.objects.enabled(shop=context["request"].shop)
            .annotate(order_lines_count=Count("order_lines"))
            .filter(
                supplier_shops__is_approved=True,
                givesome_extra__isnull=False,
                givesome_extra__allow_brand_page=True,
                givesome_extra__vendor_type=type,
            )
            .order_by("-givesome_extra__ordering")[:count]
        )

        return {"request": context["request"], "vendors": vendors, "type": type}

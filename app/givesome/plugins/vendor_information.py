# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.utils.translation import ugettext_lazy as _
from shuup.admin.supplier_provider import get_supplier
from shuup.core import cache
from shuup.xtheme import TemplatedPlugin

from givesome.models import VendorInformation


class VendorInformationPlugin(TemplatedPlugin):

    identifier = "vendor_information"
    name = _("Vendor Information")
    template_name = "givesome/plugins/vendor_information.jinja"

    def get_context_data(self, context):
        pages = cache.get(self.identifier)
        if not pages:
            pages = VendorInformation.objects.all()
            cache.set(self.identifier, pages)
        return {
            "request": context["request"],
            "vendor_information_pages": pages,
            "is_vendor": context["request"].user.is_staff or bool(get_supplier(context["request"])),
        }

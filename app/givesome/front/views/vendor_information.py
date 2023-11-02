# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from shuup.admin.supplier_provider import get_supplier

from givesome.models import VendorInformation


class VendorInformationDetailView(DetailView):

    model = VendorInformation
    template_name = "givesome/vendor_information.jinja"
    context_object_name = "vendor_information"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff or bool(get_supplier(request)):
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.admin.form_part import TemplatedFormDef
from shuup_multivendor.admin_module.form_parts.vendor import VendorBaseFormPart

from givesome.admin_module.forms.vendor_extra import GivesomeVendorExtraForm


class GivesomeVendorBaseFormPart(VendorBaseFormPart):
    priority = 1
    name = "givesome_vendor_extra"

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            GivesomeVendorExtraForm,
            template_name="givesome/admin/vendor/vendor.jinja",
            required=True,
            kwargs={"instance": self.object, "request": self.request},
        )

    def form_valid(self, form):
        form.forms[self.name].save()
        return super().form_valid(form)

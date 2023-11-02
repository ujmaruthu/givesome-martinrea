# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.admin.form_part import FormPart, TemplatedFormDef

from givesome.admin_module.forms.checkout_gif import CheckoutGifForm


class GivesomeGifBaseFormPart(FormPart):
    priority = -1000  # Show this first, no matter what

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            CheckoutGifForm,
            template_name="givesome/admin/checkout_gif/_edit_base_form.jinja",
            required=False,
            kwargs={"instance": self.object},
        )

    def form_valid(self, form):
        self.object = form["base"].save()

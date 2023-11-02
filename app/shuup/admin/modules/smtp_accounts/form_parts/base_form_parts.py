# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.modules.smtp_accounts.forms import SMTPAccountBaseForm
from shuup.core.models import SMTPAccount


class SMTPAccountBaseFormPart(FormPart):
    priority = -1000  # Show this first, no matter what
    name = "base"

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            SMTPAccountBaseForm,
            template_name="shuup/admin/smtp_accounts/_edit_base_form.jinja",
            required=True,
            kwargs={"instance": self.object},
        )

    def form_valid(self, form):
        data = form["base"].cleaned_data
        is_default_account = data["default_account"]
        old_default_account = SMTPAccount.get_default(shop=data["shop"])
        if is_default_account and old_default_account:
            old_default_account.default_account = False
            old_default_account.save()
        self.object = form["base"].save()
        if old_default_account and self.object != old_default_account:
            messages.info(self.request, _(f" {old_default_account.name} is no longer a default email account."))

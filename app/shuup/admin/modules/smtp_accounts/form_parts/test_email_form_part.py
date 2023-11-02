# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.modules.smtp_accounts.forms import TestEmailForm


class TestEmailFormPart(FormPart):
    name = "test_email"

    def get_form_defs(self):
        if not self.object.pk:
            return

        yield TemplatedFormDef(
            "test_email",
            TestEmailForm,
            template_name="shuup/admin/smtp_accounts/test_email_form.jinja",
            required=False,
            kwargs={"initial": {"recipient": "", "send": "unchecked"}},
        )

    def form_valid(self, form):
        if "test_email" not in form.forms:
            return

        test_email_form = form["test_email"]
        data = test_email_form.cleaned_data

        if data.get("send") and data.get("recipient"):
            smtp_account = self.object
            result = test_email_form.send_test_email(data["recipient"], smtp_account)

            if result:
                messages.success(self.request, _("Test email sent!"))
            else:
                messages.error(self.request, _("Test email failed!"))

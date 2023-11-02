# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib import messages
from shuup.admin.form_part import FormPart, TemplatedFormDef

from givesome.admin_module.forms.givesome_purse import GivesomePurseAllocationForm, GivesomePurseManualDonateForm


class GivesomePurseAllocationBaseFormPart(FormPart):
    priority = 0
    name = "base"

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            GivesomePurseAllocationForm,
            template_name="givesome/admin/givesome_purse/_edit_base.jinja",
            required=True,
            kwargs={
                "instance": self.object,
            },
        )

    def form_valid(self, form_group):
        self.object = form_group["base"].save()
        return self.object


class GivesomePurseAllocationManualFormPart(FormPart):
    priority = -1
    name = "manual"

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            GivesomePurseManualDonateForm,
            template_name="givesome/admin/givesome_purse/_manual_donate.jinja",
            required=True,
            kwargs={
                "instance": self.object,
            },
        )

    def form_valid(self, form_group):
        amount = form_group["manual"].save()
        if amount:
            messages.success(self.request, f"${amount} manually donated from Givesome Purse")
        return None

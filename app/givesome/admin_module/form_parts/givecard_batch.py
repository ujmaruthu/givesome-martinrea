# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _
from shuup.admin.base import Section
from shuup.admin.form_part import FormPart, TemplatedFormDef

from givesome.admin_module.forms.givecard_batch import GivecardBatchForm, MulticardBatchForm


class GivecardBatchBaseFormPart(FormPart):
    priority = -1000  # Show this first, no matter what
    form = GivecardBatchForm

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            self.form,
            template_name="givesome/admin/givecard_batch/_edit_base.jinja",
            required=True,
            kwargs={
                "instance": self.object,
            },
        )

    def form_valid(self, form_group):
        self.object = form_group["base"].save()
        return self.object


class MulticardBatchBaseFormPart(GivecardBatchBaseFormPart):
    form = MulticardBatchForm


class GivecardBatchSummarySection(Section):
    identifier = "givecard_batch_summary"
    name = _("Summary")
    icon = "fa-database"
    template = "givesome/admin/givecard_batch/_summary.jinja"
    order = 1

    @classmethod
    def visible_for_object(cls, instance):
        return bool(instance.pk)

    @classmethod
    def get_context_data(cls, instance):
        return instance

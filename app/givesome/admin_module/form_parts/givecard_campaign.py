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

from givesome.admin_module.forms.givecard_campaign import GivecardCampaignForm
from givesome.models import GivecardCampaign


class GivecardCampaignBaseFormPart(FormPart):
    priority = -1000  # Show this first, no matter what

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            GivecardCampaignForm,
            template_name="givesome/admin/givecard_campaign/_edit_base.jinja",
            required=True,
            kwargs={"instance": self.object, "request": self.request},
        )

    def form_valid(self, form_group):
        self.object = form_group["base"].save()
        return self.object


class GivecardCampaignBatchSection(Section):
    identifier = "givecard_campaign_data"
    name = _("Batches")
    icon = "fa-database"
    template = "givesome/admin/givecard_campaign/_summary.jinja"
    order = 1

    @classmethod
    def visible_for_object(cls, instance):
        return instance.batches.exists()

    @classmethod
    def get_context_data(cls, instance):
        context = {}
        context["batches"] = instance.batches.all()
        context["total"] = (
            GivecardCampaign.objects.filter(pk=instance.pk)
            .annotate_percentage_redeemed()
            .annotate_balances()
            .annotate_count_projects_donated()
            .annotate_total_amount_donated()
        ).first()
        return context

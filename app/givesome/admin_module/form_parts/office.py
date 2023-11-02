# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.admin.form_part import FormPart, TemplatedFormDef

from givesome.admin_module.forms.office import OfficeForm, SustainabilityGoalSelectionForm
from givesome.models import OfficeSustainabilityGoals


class OfficeBaseFormPart(FormPart):
    priority = -1000  # Show this first, no matter what

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            OfficeForm,
            template_name="givesome/admin/office/office_edit.jinja",
            required=True,
            kwargs={"instance": self.object, "request": self.request},
        )

    def form_valid(self, form_group):
        self.object = form_group["base"].save()
        return self.object


class OfficeSDGFormPart(FormPart):
    name = "office_sdg"
    priority = 100

    def get_initial(self):
        return OfficeSustainabilityGoals.objects.filter(office=self.object)

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            SustainabilityGoalSelectionForm,
            template_name="givesome/admin/office/office_sdgs.jinja",
            required=False,
            kwargs={"instance": self.object, "initial": self.get_initial()},
        )

    def form_valid(self, form_group):
        goals = form_group.cleaned_data.get(self.name)
        office = self.object
        project_goals, __ = OfficeSustainabilityGoals.objects.get_or_create(office=office)

        # Associate only the goals selected just now.
        if goals:
            project_goals.goals.set(goals["sustainability_goals"])
        else:
            project_goals.goals.clear()
        return super().form_valid(form_group)

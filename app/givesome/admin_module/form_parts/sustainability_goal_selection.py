# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.exceptions import ValidationError
from django.forms import forms
from shuup.admin.form_part import TemplatedFormDef
from shuup.admin.forms.fields import Select2ModelMultipleField
from shuup_multivendor.admin_module.form_parts.vendor import VendorBaseFormPart

from givesome.models import SustainabilityGoal, VendorSustainabilityGoals


class SustainabilityGoalSelectionFormSet(forms.Form):
    sustainability_goals = Select2ModelMultipleField(
        SustainabilityGoal,
        required=False,
        help_text="Begin typing key words relating to the Sustainable Development Goals you wish to feature.",
    )

    def __init__(self, *args, **kwargs):
        existing_goals = []
        if kwargs.get("initial"):
            existing_goals = [(goal.id, goal) for goal in kwargs.pop("initial").first().goals.all()]
        super().__init__(*args, **kwargs)
        # Note: odd as it looks, the following combination of initial/choices is necessary for the initial
        # value to render properly.
        self.fields["sustainability_goals"].initial = [goal[0] for goal in existing_goals]
        self.fields["sustainability_goals"].widget.choices = existing_goals
        # Show results immediately on open
        self.fields["sustainability_goals"].widget.attrs["data-minimum-input-length"] = 0

    def clean_sustainability_goals(self):
        goals = self.cleaned_data["sustainability_goals"]
        if len(goals) > 3:
            raise ValidationError("Please choose only three Sustainable Development Goals")
        return goals


class VendorSustainabilityGoalFormPart(VendorBaseFormPart):
    priority = 4
    name = "sustainability goals"

    def get_initial(self):
        return VendorSustainabilityGoals.objects.filter(vendor=self.object)

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            SustainabilityGoalSelectionFormSet,
            template_name="givesome/admin/sustainability_goal/sustainability_goal_vendor_selection.jinja",
            required=False,
            kwargs={"initial": self.get_initial()},
        )

    def form_valid(self, form):
        goals = form.cleaned_data.get(self.name)
        vendor = form.form_defs["base"].kwargs["instance"]
        vendor_goals, __ = VendorSustainabilityGoals.objects.get_or_create(vendor=vendor)
        # Associate only the goals selected just now.
        if goals:
            vendor_goals.goals.set(goals["sustainability_goals"])
        else:
            vendor_goals.goals.clear()
        return super().form_valid(form)

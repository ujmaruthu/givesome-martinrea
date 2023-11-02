# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from shuup.admin.forms import ShuupAdminForm
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView

from givesome.models import SustainabilityGoal


class SustainabilityGoalForm(ShuupAdminForm):
    class Meta:
        model = SustainabilityGoal
        fields = ("identifier", "name", "description", "image")


class SustainabilityGoalEditView(CreateOrUpdateView):
    model = SustainabilityGoal
    form_class = SustainabilityGoalForm
    template_name = "givesome/admin/sustainability_goal/sustainability_goal_edit.jinja"
    context_object_name = "sustainability_goal"

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        delete_url = None
        sustainability_goal = self.get_object()
        if sustainability_goal and sustainability_goal.pk:
            delete_url = reverse("shuup_admin:sustainability_goal.delete", kwargs={"pk": sustainability_goal.pk})
        return get_default_edit_toolbar(self, save_form_id, delete_url=delete_url)


class SustainabilityGoalListView(PicotableListView):
    model = SustainabilityGoal
    default_columns = [
        Column("identifier", _("Identifier"), ordering=2, sortable=False),
        Column(
            "name",
            _("Name"),
            ordering=1,
            sortable=True,
            filter_config=TextFilter(
                filter_field="sustainability_goal__translations__name", placeholder="Filter by name..."
            ),
        ),
        Column("description", _("Description"), ordering=3, sortable=False),
        Column("image", _("Image"), ordering=4, sortable=False, raw=True),
    ]
    toolbar_buttons_provider_key = "sustainability_goal_list_toolbar_provider"
    mass_actions_provider_key = "sustainability_goal_list_mass_actions_provider"


class SustainabilityGoalDeleteView(DetailView):
    model = SustainabilityGoal

    def get_success_url(self):
        return reverse("shuup_admin:sustainability_goal.list")

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        messages.success(request, _("SDG has been marked deleted."))
        return HttpResponseRedirect(self.get_success_url())

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.picotable import Column, DateRangeFilter, TextFilter
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView

from givesome.admin_module.form_parts.givecard_campaign import (
    GivecardCampaignBaseFormPart,
    GivecardCampaignBatchSection,
)
from givesome.admin_module.utils import BoolFilter
from givesome.models import GivecardCampaign


class GivecardCampaignEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = GivecardCampaign
    template_name = "givesome/admin/givecard_campaign/edit.jinja"
    context_object_name = "givecard_campaign"
    add_form_errors_as_messages = True
    base_form_part_classes = [
        GivecardCampaignBaseFormPart,
    ]

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        delete_url = None
        givecard_campaign = self.get_object()
        if givecard_campaign and givecard_campaign.pk:
            delete_url = reverse("shuup_admin:givecard_campaign.delete", kwargs={"pk": givecard_campaign.pk})
        return get_default_edit_toolbar(self, save_form_id, delete_url=delete_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        context["sections"] = []

        sections = [GivecardCampaignBatchSection]
        for section in sections:
            if section.visible_for_object(self.object):
                context["sections"].append(section)
                context[section.identifier] = section.get_context_data(self.object)
        return context

    def form_valid(self, form):
        return self.save_form_parts(form)


class GivecardCampaignListView(PicotableListView):
    model = GivecardCampaign
    url_identifier = "givecard_campaign"
    columns = [
        Column(
            "image", _("Image"), display="get_image", class_name="text-center", raw=True, ordering=1, sortable=False
        ),
        Column(
            "identifier",
            _("ID"),
            ordering=2,
            sortable=True,
            filter_config=TextFilter(filter_field="identifier", placeholder="Filter by Identifier..."),
        ),
        Column(
            "name",
            _("Name"),
            ordering=3,
            sortable=True,
            filter_config=TextFilter(filter_field="translations__name", placeholder="Filter by name..."),
        ),
        Column(
            "supplier",
            _("Branded Vendor"),
            ordering=4,
            sortable=True,
            filter_config=TextFilter(filter_field="supplier__name", placeholder="Filter by Branded Vendor..."),
        ),
        Column(
            "group",
            _("Group"),
            ordering=5,
            sortable=True,
            filter_config=TextFilter(filter_field="group__name", placeholder="Filter by Group..."),
        ),
        Column("created_on", _("Created on"), ordering=8, sortable=True, filter_config=DateRangeFilter()),
        Column("archived", _("Archived"), ordering=10, sortable=True, filter_config=BoolFilter()),
    ]

    def get_image(self, instance):
        if instance.image:
            thumbnail = instance.get_image_thumbnail()
            if thumbnail:
                return "<img src='{}{}'>".format(settings.MEDIA_URL, thumbnail)
        return "<img src='%s'>" % static("shuup_admin/img/no_image_thumbnail.png")

    def __init__(self):
        pass  # Keep columns as-is


class GivecardCampaignDeleteView(DetailView):
    model = GivecardCampaign

    def get_success_url(self):
        return reverse("shuup_admin:givecard_campaign.list")

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        messages.success(request, _("Givecard Campaign has been deleted."))
        return HttpResponseRedirect(self.get_success_url())

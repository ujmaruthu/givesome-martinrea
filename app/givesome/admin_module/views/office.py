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
from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.toolbar import URLActionButton, get_default_edit_toolbar
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView

from givesome.admin_module.form_parts.office import OfficeBaseFormPart, OfficeSDGFormPart
from givesome.models import GivesomeOffice


class OfficeEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = GivesomeOffice
    template_name = "givesome/admin/office/edit.jinja"
    context_object_name = "office"
    add_form_errors_as_messages = True
    base_form_part_classes = [
        OfficeBaseFormPart,
        OfficeSDGFormPart,
    ]

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        delete_url = None
        office = self.get_object()
        if office and office.pk:
            delete_url = reverse("shuup_admin:office.delete", kwargs={"pk": office.pk})
        toolbar = get_default_edit_toolbar(self, save_form_id, delete_url=delete_url)
        if office and office.pk:
            toolbar.append(
                URLActionButton(
                    url=reverse("shuup_admin:office_project_promote.edit", kwargs={"pk": office.pk}),
                    text="Promoted Projects",
                    tooltip=_("Manage office promoted projects"),
                    icon="fa fa-handshake-o",
                    extra_css_class="btn-inverse",
                )
            )
        return toolbar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context

    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_queryset(self):
        qs = super().get_queryset()
        supplier = get_supplier(self.request)
        if supplier:
            qs = qs.filter(supplier=supplier)
        return qs


class OfficeListView(PicotableListView):
    model = GivesomeOffice
    url_identifier = "office"
    columns = [
        Column("id", _("ID"), ordering=1, sortable=True),
        Column(
            "name",
            _("Name"),
            ordering=2,
            sortable=True,
            filter_config=TextFilter(filter_field="name", placeholder="Filter by name..."),
        ),
        Column(
            "supplier",
            _("Branded Vendor"),
            ordering=3,
            sortable=True,
            filter_config=TextFilter(filter_field="supplier__name", placeholder="Filter by Branded Vendor..."),
        ),
        Column(
            "parent__name",
            _("Parent"),
            ordering=5,
            sortable=True,
            filter_config=TextFilter(filter_field="parent__name", placeholder="Filter by Parent name..."),
        ),
        Column(
            "level",
            _("Level"),
            ordering=6,
            sortable=True,
        ),
        Column(
            "disabled",
            _("Disabled"),
            ordering=10,
            sortable=True,
        ),
    ]

    def __init__(self):
        """To keep columns as-is"""
        pass

    def get_queryset(self):
        qs = super().get_queryset()
        supplier = get_supplier(self.request)
        if supplier:
            qs = qs.filter(supplier=supplier)
        return qs


class OfficeDeleteView(DetailView):
    model = GivesomeOffice

    def get_success_url(self):
        return reverse("shuup_admin:office.list")

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        messages.success(request, _("Office has been deleted."))
        return HttpResponseRedirect(self.get_success_url())

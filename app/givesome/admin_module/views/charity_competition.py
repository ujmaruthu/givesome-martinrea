# -*- coding: utf-8 -*-
# Addition to Shuup owned by Givesome...
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.toolbar import (
    DropdownActionButton,
    Toolbar,
    URLActionButton,
    get_default_edit_toolbar,
    JavaScriptActionButton,
    PostActionButton,
)
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup.core.models import ProductMode, ShopProduct, ShopProductVisibility, Supplier
from shuup.front.utils.sorts_and_filters import bump_product_queryset_cache
from shuup_multivendor.admin_module.views.products import ProductListView
from shuup_multivendor.utils.product import filter_approved_shop_products

from givesome.admin_module.forms.shop_settings import givesome_promote_invisible
from givesome.enums import VendorExtraType
from givesome.models import GivesomeOffice, GivesomePromotedProduct, GivesomeCompetition

from givesome.admin_module.form_parts.givesome_competition import (
    GivesomeCompetitionBaseFormPart,
)


class CharityCompetitionListView(PicotableListView):
    model = GivesomeCompetition
    url_identifier = "Competitions List"
    columns = [
        Column(
            "slug",
            _("Name"),
            ordering=1,
            sortable=True,
            filter_config=TextFilter(
                filter_field="name", placeholder="Filter by name..."
            ),
        ),
        Column(
            "competition_runner",
            _("Competition Runner"),
            ordering=2,
            sortable=True,
            filter_config=TextFilter(
                filter_field="vendor", placeholder="Filter by competition runner..."
            ),
        ),
        Column(
            "start_date",
            _("Start Date"),
            ordering=3,
            sortable=True,
            filter_config=TextFilter(
                filter_field="start_date", placeholder="Filter by start date..."
            ),
        ),
        Column(
            "end_date",
            _("End Date"),
            ordering=4,
            sortable=True,
            filter_config=TextFilter(
                filter_field="end_date", placeholder="Filter by end date..."
            ),
        ),
    ]

    def __init__(self):
        # Don't modify picotable columns
        pass

    def get_object_url(self, instance):
        return (
            reverse(
                "shuup_admin:charity_competition.edit", kwargs={"pk": instance.pk}
            ),
        )

    def get_toolbar(self):
        return []

    def get_queryset(self):
        qs = super().get_queryset()
        return qs


class CharityCompetitionEditView(
    SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView
):
    model = GivesomeCompetition
    template_name = "givesome/admin/givesome_competition/edit.jinja"
    context_object_name = "givesome_competition"
    add_form_errors_as_messages = True

    base_form_part_classes = [GivesomeCompetitionBaseFormPart]
    new_object_title = _("New Givecard Competition")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        if not self.object.pk:
            context["title"] = self.new_object_title

        context["sections"] = []
        sections = []
        for section in sections:
            if section.visible_for_object(self.object):
                context["sections"].append(section)
                context[section.identifier] = section.get_context_data(self.object)

        return context

    def form_valid(self, form):
        competition = self.save_form_parts(form)
        return HttpResponseRedirect("")

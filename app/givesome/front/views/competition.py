# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from parler.utils import get_active_language_choices
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import Order, OrderLine, get_person_contact
from shuup.front.forms.product_list_modifiers import CommaSeparatedListField

from givesome.admin_module.forms.shop_settings import givesome_fully_funded_display_days
from givesome.enums import VendorExtraType
from givesome.front.utils import filter_valid_projects
from givesome.models import GivesomeCompetition


class GivesomeCompetitionView(DetailView):
    model = GivesomeCompetition
    template_name = "givesome/competition/league_table.jinja"

    def get_context_data(self, **kwargs):
        start_date = kwargs["object"].start_date
        end_date = kwargs["object"].end_date
        competition_runner = kwargs["object"].competition_runner

        context = {}
        context["active"] = kwargs["object"].active
        context["authwall"] = False
        all_competitors = kwargs["object"].competitors.all()
        if context["active"] and not self.request.user in all_competitors:
            context["authwall"] = True
            self.template_name = "givesome/competition/authwall.jinja"
            return context
        elif not context["active"]:
            self.template_name = "givesome/competition/inactive.jinja"
            return context
        context["competition_key"] = kwargs["object"].competition_key
        context["competition_name"] = kwargs["object"].slug
        context["competition_runner"] = competition_runner
        context["start_date"] = start_date.strftime("%Y/%m/%d")
        context["end_date"] = end_date.strftime("%Y/%m/%d")
        competitors = []
        for i in all_competitors:
            contact = get_person_contact(i)
            first_name = contact.first_name.capitalize()
            last_name = contact.last_name.capitalize()
            user_id = contact.id

            if not (first_name and last_name):
                continue
            customer_orders = OrderLine.objects.select_related("order").filter(
                order__customer_id=user_id
            )
            score = 0
            orders = 0
            for j in customer_orders:
                if competition_runner and not competition_runner.id == j.supplier_id:
                    continue
                if start_date <= j.created_on <= end_date:
                    score += j.quantity * j.base_unit_price_value
                    orders += 1
            competitors += [
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "score": int(score),
                    "orders": orders,
                    "is_user": self.request.user == i,
                }
            ]
        context["competitors"] = sorted(
            competitors, reverse=True, key=lambda d: d["score"]
        )
        return context

    def post(self, request, *args, **kwargs) -> JsonResponse:
        user = request.user
        code = request.POST.get("code")
        slug = kwargs.get("slug")

        competition = GivesomeCompetition.objects.get(slug=slug)
        competition_key = competition.competition_key

        if not request.user.is_authenticated:
            messages.warning(
                request, "Please log in or create an account to join the competition"
            )
            return HttpResponseRedirect("")
        elif not competition_key == code:
            messages.warning(request, "Incorrect competition key provided.")
            return HttpResponseRedirect("")
        competition.competitors.add(request.user)
        competition.save()
        messages.info(request, f"Congratulations! You have joined {slug} competition!")
        return HttpResponseRedirect("")

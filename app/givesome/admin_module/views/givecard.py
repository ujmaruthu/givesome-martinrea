# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.http.response import Http404
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from shuup.admin.base import MenuEntry
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView

from givesome.admin_module.utils import HasValueFilter
from givesome.models import Givecard, GivecardBatch


class GivecardListView(PicotableListView):
    model = Givecard
    url_identifier = "givecard"
    columns = [
        Column(
            "code",
            _("PIN"),
            ordering=1,
            sortable=True,
            filter_config=TextFilter(filter_field="code", placeholder="Filter by PIN..."),
        ),
        Column(
            "user",
            _("User"),
            ordering=2,
            sortable=True,
            filter_config=TextFilter(filter_field="user__username", placeholder="Filter by User..."),
        ),
        Column(
            "redeemed_on",
            _("Redeemed on"),
            ordering=3,
            sortable=True,
            filter_config=HasValueFilter(
                filter_field="redeemed_on", labels={"true": _("Redeemed"), "false": _("Not Redeemed")}
            ),
        ),
        Column("balance", _("Balance"), display="get_balance", ordering=4, sortable=True),
        Column(
            "automatically_donated",
            _("Automatically donated"),
            ordering=5,
            sortable=True,
            filter_config=HasValueFilter(
                filter_field="automatically_donated", labels={"true": "True", "false": "False"}
            ),
        ),
    ]

    def __init__(self):
        """To keep columns as-is"""
        pass

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # Hide code column for Multicards
        # This can't be done in __init__() as it does not have access to batch pk
        if GivecardBatch.objects.filter(pk=self.kwargs["pk"], code__isnull=False).exists():
            self.columns = [column for column in self.columns if column.id != "code"]

    def get_balance(self, instance):
        """Show 0 balance. Otherwise field would be blank"""
        if instance.balance == 0:
            return "0"
        return instance.balance

    def get_breadcrumb_parents(self):
        return [
            MenuEntry(
                text=GivecardBatch.objects.get(pk=self.kwargs["pk"]),
                url=reverse("shuup_admin:givecard_batch.edit", kwargs={"pk": self.kwargs["pk"]}),
            ),
            MenuEntry(
                text=force_text(self.model._meta.verbose_name_plural).title(),
                url=reverse("shuup_admin:givecard.list", kwargs={"pk": self.kwargs["pk"]}),
            ),
        ]

    def get_queryset(self):
        """Filter Givecards belonging to selected Batch"""
        qs = super().get_queryset()
        qs = qs.filter(batch__pk=self.kwargs["pk"])
        return qs


class GivecardGenerateView(View):
    def post(self, request, *args, **kwargs):
        if get_supplier(self.request):
            raise Http404()

        batch = GivecardBatch.objects.get(pk=request.POST.get("batchId"))
        if not batch:
            raise Http404()

        try:
            batch.generate_givecards()
        except ValidationError:
            raise Http404()

        return JsonResponse({"ok": True})

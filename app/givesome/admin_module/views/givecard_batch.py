# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import csv
from io import StringIO

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import DetailView
from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.toolbar import (
    JavaScriptActionButton,
    NewActionButton,
    PostActionButton,
    Toolbar,
    URLActionButton,
    get_default_edit_toolbar,
)
from shuup.admin.utils.picotable import ChoicesFilter, Column, TextFilter
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup.core.models import get_person_contact

from givesome.admin_module.form_parts.givecard_batch import (
    GivecardBatchBaseFormPart,
    GivecardBatchSummarySection,
    MulticardBatchBaseFormPart,
)
from givesome.admin_module.utils import BoolFilter, HasValueFilter
from givesome.enums import GivecardBatchExpiryType, GivecardDonateRestrictionType
from givesome.models import Givecard, GivecardBatch, GivecardPurseCharge, PurchaseReportData


class GivecardBatchEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = GivecardBatch
    template_name = "givesome/admin/givecard_batch/edit.jinja"
    context_object_name = "givecard_batch"
    add_form_errors_as_messages = True

    base_form_part_classes = [GivecardBatchBaseFormPart]
    new_object_title = _("New Givecard Batch")

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        delete_url = None
        givecard_batch = self.get_object()
        if (
            givecard_batch
            and givecard_batch.pk
            and not PurchaseReportData.objects.filter(givecard__batch__id=givecard_batch.pk).exists()
            and not GivecardPurseCharge.objects.filter(batch__id=givecard_batch.pk).exists()
        ):
            delete_url = reverse("shuup_admin:givecard_batch.delete", kwargs={"pk": givecard_batch.pk})
        toolbar = get_default_edit_toolbar(self, save_form_id, delete_url=delete_url)
        if givecard_batch and givecard_batch.pk:
            if givecard_batch.givecards.all().exists():
                toolbar.append(
                    URLActionButton(
                        url=reverse("shuup_admin:givecard.list", kwargs={"pk": givecard_batch.pk}),
                        text="View Givecards",
                        tooltip=_("View Generated Givecards"),
                        icon="fa fa-ticket",
                        extra_css_class="btn-inverse",
                    )
                )
                toolbar.append(
                    URLActionButton(
                        url=reverse("download-batch", kwargs={"pk": self.kwargs["pk"]}),
                        text="Download Givecards",
                        tooltip=_("Download generated Givecards as a CSV file"),
                        icon="fa fa-download",
                        extra_css_class="btn-inverse",
                        required_permissions=["givecard.list"],
                    )
                )
                if givecard_batch.is_nullifiable():
                    toolbar.append(
                        PostActionButton(
                            post_url=reverse("nullify-batch", kwargs={"pk": self.kwargs["pk"]}),
                            text="Nullify Givecards",
                            tooltip=_(
                                "Once the batch balance has been handled off-platform, nullify the balance here."
                            ),
                            icon="fa fa-check-square",
                            extra_css_class="btn-inverse",
                            confirm=_("Have you handled the funds for %s?") % givecard_batch,
                            required_permissions=["givecard_batch.edit"],
                        )
                    )
            else:
                toolbar.append(
                    JavaScriptActionButton(
                        onclick=f"generateGivecards({givecard_batch.id})",
                        icon="fa fa-ticket",
                        text=_("Generate Givecards"),
                        extra_css_class="btn-inverse givecard_toolbar_button",
                    )
                )
        return toolbar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        if not self.object.pk:
            context["title"] = self.new_object_title

        context["sections"] = []
        sections = [GivecardBatchSummarySection]
        for section in sections:
            if section.visible_for_object(self.object):
                context["sections"].append(section)
                context[section.identifier] = section.get_context_data(self.object)

        return context

    def form_valid(self, form):
        return self.save_form_parts(form)


class MulticardBatchEditView(GivecardBatchEditView):
    """Used only for creating new Multicard Batches"""

    base_form_part_classes = [MulticardBatchBaseFormPart]
    new_object_title = _("New Multicard Batch")


class GivecardBatchListView(PicotableListView):
    model = GivecardBatch
    url_identifier = "givecard_batch"
    columns = [
        Column(
            "campaign",
            _("Campaign"),
            ordering=1,
            sortable=True,
            display="get_campaign",
            filter_config=TextFilter(
                filter_field="campaign__identifier", placeholder="Filter by Campaign identifier..."
            ),
        ),
        Column(
            "supplier",
            _("Vendor"),
            ordering=2,
            sortable=True,
            filter_config=TextFilter(filter_field="supplier__name", placeholder="Filter by Branded Vendor..."),
        ),
        Column(
            "office",
            _("Office"),
            ordering=3,
            sortable=True,
            display="get_office",
            filter_config=TextFilter(filter_field="office__name", placeholder="Filter by Office..."),
        ),
        Column(
            "multicard_code",
            _("PIN"),
            ordering=4,
            sortable=False,
            display="get_code",
            filter_config=HasValueFilter(
                filter_field="code", labels={"true": _("Multicard"), "false": _("Unique Givecard")}
            ),
        ),
        Column(
            "restriction_type",
            _("Restriction"),
            ordering=5,
            sortable=True,
            display="get_restriction",
            filter_config=ChoicesFilter(
                filter_field="restriction_type", choices=GivecardDonateRestrictionType.choices()
            ),
        ),
        Column(
            "amount",
            _("Quantity"),
            ordering=10,
            sortable=True,
            filter_config=TextFilter(filter_field="amount", placeholder="Filter by Amount..."),
        ),
        Column(
            "value",
            _("Value"),
            ordering=11,
            sortable=True,
            filter_config=TextFilter(filter_field="value", placeholder="Filter by $ Value..."),
        ),
        Column("used", _("Used %"), display="get_used_percentage", ordering=12, sortable=False),
        Column("generated_on", _("Generated on"), ordering=20, sortable=True),
        Column("redemption_start_date", _("Redeem start"), ordering=21, sortable=True),
        Column("expiration_date", _("Expires"), ordering=23, sortable=True),
        Column(
            "expiry_type",
            _("Expiry type"),
            ordering=24,
            sortable=True,
            filter_config=ChoicesFilter(filter_field="expiry_type", choices=GivecardBatchExpiryType.choices()),
        ),
        Column("archived", _("Archived"), ordering=10, sortable=True, filter_config=BoolFilter()),
    ]

    def __init__(self):
        """This is to keep columns as-is. super()__init__() modifies columns"""
        pass

    def get_campaign(self, instance):
        return instance.campaign.identifier if instance.campaign else "-"

    def get_office(self, instance):
        return instance.office.name if instance.office else "-"

    def get_code(self, instance):
        """Required, because "code" column is a highlighted by picotable. (added as a big filter to the top)"""
        return instance.code if instance.code is not None else "-"

    def get_restriction(self, instance):
        if instance.restriction_type != GivecardDonateRestrictionType.DISABLED:
            return instance.restriction_type.label
        return "-"

    def get_used_percentage(self, instance):
        """% of Batch's total balance is used"""
        sum_balance = instance.total_balance
        if sum_balance == 0:
            return "-"
        return f"{int(100 - sum_balance / (instance.value * instance.amount) * 100)}%"

    def get_toolbar(self):
        """Add `New Multicard Batch` and `New Givecard Batch` buttons"""
        toolbar = Toolbar()

        model = self.model
        toolbar.append(NewActionButton.for_model(model=model, url="new", text=_("New Givecard Batch")))
        toolbar.append(
            NewActionButton.for_model(model=model, url="/admin/multicard_batch/new", text=_("New Multicard Batch"))
        )
        toolbar.extend(Toolbar.for_view(self))
        return toolbar


class GivecardBatchDeleteView(DetailView):
    model = GivecardBatch

    def get_success_url(self):
        return reverse("shuup_admin:givecard_batch.list")

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        messages.success(request, _("Givecard Batch has been deleted."))
        return HttpResponseRedirect(self.get_success_url())


class GivecardBatchDownloadView(View):

    headers = ["Code", "User", "Redeemed on", "Balance", "Automatically donated"]

    def write_csv(self):
        """Create an in-memory csv file detailing all the Givecard data points."""
        givecards_csv = StringIO()
        writer = csv.DictWriter(givecards_csv, fieldnames=self.headers)
        writer.writeheader()

        givecards = Givecard.objects.filter(batch_id=self.kwargs["pk"]).select_related("batch")
        for card in givecards:
            writer.writerow(
                {
                    self.headers[0]: card.code if card.code is not None else card.batch.code,
                    self.headers[1]: card.user,
                    self.headers[2]: card.redeemed_on,
                    self.headers[3]: card.balance,
                    self.headers[4]: card.automatically_donated,
                }
            )
        return givecards_csv

    def get(self, request, *args, **kwargs):
        resp = HttpResponse(
            self.write_csv().getvalue(), content_type="text/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        resp["Content-Disposition"] = "attachment; filename=Givecard Batch {}.xlsx".format(self.kwargs["pk"])
        return resp


def nullify_batch(request, *args, **kwargs):
    if request.method == "POST":
        batch = GivecardBatch.objects.filter(pk=kwargs["pk"]).first()
        if batch is None:
            raise Http404()

        try:
            batch.nullify(get_person_contact(request.user))
        except ValidationError as e:
            messages.warning(request, _("A problem occurred: %s") % e.message)

        messages.success(request, _("Givecard Batch has been nullified."))
        return HttpResponseRedirect(reverse("shuup_admin:givecard.list", kwargs={"pk": kwargs["pk"]}))

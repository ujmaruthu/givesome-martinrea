# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from shuup.admin.form_part import TemplatedFormDef
from shuup.core.models import Product, Supplier
from shuup.simple_supplier.admin_module.forms import SimpleSupplierForm, SimpleSupplierFormPart
from shuup.simple_supplier.utils import get_stock_information_div_id
from shuup.utils.analog import LogEntryKind
from shuup.utils.models import get_data_dict


class GoalProgressAdjustmentForm(forms.Form):
    delta = forms.DecimalField(label=_("Quantity to add"))

    def clean_delta(self):
        delta = self.cleaned_data.get("delta")
        if delta is None or delta == 0:
            raise ValidationError(_("Please enter a non-zero amount."), code="stock_delta_zero")
        return delta


class GivesomeSimpleSupplierForm(SimpleSupplierForm):
    def get_stock_information(self, supplier, project):
        return get_progress_html(supplier, project)

    def get_stock_adjustment_form(self, supplier, product):
        return get_progress_adjustment_div(supplier, product, self.request)


class GivesomeSimpleSupplierFormPart(SimpleSupplierFormPart):
    form = GivesomeSimpleSupplierForm

    def get_form_defs(self):
        # Don't show if product is new
        if (
            self.object.pk
            and hasattr(self.object.product, "project_extra")
            and self.object.product.project_extra.goal_amount > 0
        ):
            yield TemplatedFormDef(
                name=self.name,
                form_class=self.form,
                template_name="shuup/simple_supplier/admin/product_form_part.jinja",
                required=False,
                kwargs={"product": self.object.product, "request": self.request},
            )


def get_progress_html(supplier, project):
    context = {
        "div_id": get_stock_information_div_id(supplier, project),
        "goal_amount": project.project_extra.goal_amount,
        "goal_progress_amount": project.project_extra.goal_progress_amount,
        "goal_progress_percentage": project.project_extra.goal_progress_percentage,
    }
    return render_to_string("shuup/simple_supplier/admin/stock_information.jinja", context)


def get_progress_adjustment_div(supplier, project, request):
    context = {"supplier": supplier, "project": project, "adjustment_form": GoalProgressAdjustmentForm()}
    return render_to_string("shuup/simple_supplier/admin/add_stock_form.jinja", context=context, request=request)


class GivesomeProcessStockFormView(FormView):
    form_class = GoalProgressAdjustmentForm

    def post(self, request, *args, **kwargs):
        return super(GivesomeProcessStockFormView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        charity = Supplier.objects.filter(id=self.kwargs["supplier_id"]).first()
        project = Product.objects.filter(id=self.kwargs["project_id"]).first()

        progress_adjustment = charity.adjust_stock(
            project.id, delta=form.cleaned_data.get("delta") * -1, purchase_price=1, created_by=self.request.user
        )
        adjustment = progress_adjustment.delta * -1

        project.add_log_entry(
            'Givesome staff "{}" added ${} to project progress.'.format(self.request.user.username, adjustment),
            user=self.request.user,
            identifier="givesome_progress_amount_change",
            kind=LogEntryKind.EDIT,
            extra=get_data_dict(project, force_text_for_value=True),
        )
        success_message = get_success_msg_obj(self.request, charity, project, adjustment)
        return JsonResponse(success_message, status=200, safe=False)


def get_success_msg_obj(request, charity, project, qty):
    success = {
        "stockInformationDiv": "#%s" % get_stock_information_div_id(charity, project),
        "updatedStockInformation": get_progress_html(charity, project),
        "updatedStockManagement": get_progress_adjustment_div(charity, project, request),
    }
    kwargs = {"delta": qty, "project_name": project.name, "charity_name": charity.name}
    success["message"] = _("Success! Added $ %(delta)s towards %(project_name)s by %(charity_name)s.") % kwargs

    return success

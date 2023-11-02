# -*- coding: utf-8 -*-
# Addition to Shuup owned by Givesome...
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import DeleteView
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
from givesome.models.reports import PurchaseReportData
from shuup.core.models import Order, OrderLine, OrderStatusHistory, Payment
from shuup.simple_supplier.models import StockCount


class ManageOrdersListView(PicotableListView):
    model = Order
    url_identifier = "Recent Orders"
    columns = [
        Column(
            "id",
            _("ID"),
            ordering=1,
            sortable=True,
            filter_config=TextFilter(filter_field="id", placeholder="Filter by id..."),
        ),
        Column(
            "created_on",
            _("Order Date"),
            ordering=2,
            sortable=True,
            filter_config=TextFilter(
                filter_field="created", placeholder="Filter by date of creation..."
            ),
        ),
        Column(
            "email",
            _("Email"),
            ordering=3,
            sortable=True,
            filter_config=TextFilter(
                filter_field="email", placeholder="Filter by email used..."
            ),
        ),
        Column(
            "payment_method_name",
            _("Payment Method"),
            ordering=4,
            sortable=True,
            filter_config=TextFilter(
                filter_field="Payment method",
                placeholder="Filter by payment method used...",
            ),
        ),
        Column(
            "taxful_total_price_value",
            _("Total"),
            ordering=5,
            sortable=True,
            filter_config=TextFilter(
                filter_field="total_cost", placeholder="Filter by total cost..."
            ),
        ),
        Column(
            "ip_address",
            _("IP Address"),
            ordering=6,
            sortable=True,
            filter_config=TextFilter(
                filter_field="ip_address", placeholder="Filter by IP address..."
            ),
        ),
        Column(
            "deleted",
            _("Deleted?"),
            ordering=7,
            sortable=True,
            filter_config=TextFilter(
                filter_field="deleted", placeholder="Filter by deleted orders..."
            ),
        ),
    ]

    def __init__(self):
        # Don't modify picotable columns
        pass

    def get_object_url(self, instance):
        return (reverse("shuup_admin:manage_orders.edit", kwargs={"pk": instance.pk}),)

    def get_toolbar(self):
        return []

    def get_queryset(self):
        qs = super().get_queryset()
        return qs


class ManageOrdersEditView(DeleteView):
    model = Order
    template_name = "givesome/admin/givesome_manage_order/delete.jinja"
    context_object_name = "givesome_order"
    add_form_errors_as_messages = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        context["givesome_order"].product = (
            OrderLine.objects.filter(order_id=context["givesome_order"].id).first().text
        )
        return context

def delete_order(request, **kwargs):
    success_url = reverse_lazy("shuup_admin:manage_orders.list")

    order_id = kwargs['pk']

    order = Order.objects.filter(id=order_id)
    order_line = OrderLine.objects.filter(order_id=order_id)
    order_status_history = OrderStatusHistory.objects.filter(order_id=order_id)

    for item in order_line:
        if item.product:
            product = item.product
            break

    if not product:
        raise ValueError("Product not recorded in orderline")

    stock_count = StockCount.objects.filter(product_id = product.id).first()
    stock_count.logical_count = stock_count.logical_count + order.first().taxful_total_price_value

    payments = Payment.objects.filter(order_id=order_id)
    for p in payments:
        PurchaseReportData.objects.filter(payment_id=p.id).delete()

    payments.delete()
    order_status_history.delete()
    order_line.delete()
    order.delete()

    stock_count.save()
    return HttpResponseRedirect(success_url)

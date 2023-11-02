# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db.models import Q
from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.toolbar import DropdownActionButton, Toolbar, URLActionButton
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import ProductMode, ShopProduct, ShopProductVisibility, Supplier
from shuup.front.utils.sorts_and_filters import bump_product_queryset_cache
from shuup_multivendor.admin_module.views.products import ProductListView
from shuup_multivendor.utils.product import filter_approved_shop_products

from givesome.admin_module.forms.shop_settings import givesome_promote_invisible
from givesome.enums import VendorExtraType
from givesome.models import GivesomeOffice, GivesomePromotedProduct


class OfficeProjectPromoteListView(PicotableListView):
    model = GivesomeOffice
    url_identifier = "office_project_promote"
    default_columns = [
        Column(
            "name",
            _("Name"),
            ordering=1,
            sortable=True,
            filter_config=TextFilter(filter_field="name", placeholder="Filter by name..."),
        ),
        Column(
            "supplier",
            _("Branded Vendor"),
            ordering=2,
            sortable=True,
            filter_config=TextFilter(filter_field="supplier__name", placeholder="Filter by Branded Vendor..."),
        ),
    ]

    def get_object_url(self, instance):
        return (reverse("shuup_admin:office_project_promote.edit", kwargs={"pk": instance.pk}),)

    def get_toolbar(self):
        return []

    def get_queryset(self):
        qs = super().get_queryset()
        supplier = get_supplier(self.request)
        if supplier:
            qs = qs.filter(supplier=supplier)
        return qs


class VendorProjectPromoteListView(PicotableListView):
    model = Supplier
    url_identifier = "vendor_project_promote"
    columns = [
        Column(
            "name",
            _("Name"),
            ordering=1,
            sortable=True,
            filter_config=TextFilter(filter_field="name", placeholder="Filter by name..."),
        ),
        Column(
            "vendor_type",
            _("Vendor type"),
            ordering=2,
            sortable=True,
            sort_field="givesome_extra__vendor_type",
            display="get_vendor_type",
        ),
    ]

    def __init__(self):
        # Don't modify picotable columns
        pass

    def get_vendor_type(self, instance):
        return instance.givesome_extra.vendor_type.label

    def get_object_url(self, instance):
        return (reverse("shuup_admin:vendor_project_promote.edit", kwargs={"pk": instance.pk}),)

    def get_toolbar(self):
        return []

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(
                supplier_shops__is_approved=True, givesome_extra__isnull=False, givesome_extra__allow_brand_page=True
            )
            .prefetch_related("givesome_extra")
        )
        supplier = get_supplier(self.request)
        if supplier:
            qs = qs.filter(id=supplier.id)
        return qs

    def dispatch(self, request, *args, **kwargs):
        supplier = get_supplier(self.request)
        if supplier:  # Redirect user to their promotion page directly
            return redirect(reverse("shuup_admin:vendor_project_promote.edit", kwargs={"pk": supplier.pk}))
        return super().dispatch(request, *args, **kwargs)


class ProjectPromoteEditView(ProductListView):
    default_columns = [
        Column(
            "primary_image",
            _("Primary Image"),
            display="get_primary_image",
            class_name="text-center",
            raw=True,
            ordering=1,
            sortable=False,
        ),
        Column(
            "name",
            _("Name"),
            display="get_name",
            raw=True,
            filter_config=TextFilter(filter_field="product__translations__name", placeholder=_("Filter by name...")),
        ),
        Column(
            "description",
            _("Short Description"),
            display="get_description",
        ),
        Column(
            "supplier",
            _("Charity"),
            display="get_supplier_name",
            filter_config=TextFilter(filter_field="suppliers__name", placeholder=_("Filter by charity...")),
        ),
        Column(
            "primary_category",
            _("Location"),
            display=(lambda instance: instance.primary_category.name if instance.primary_category else None),
            filter_config=TextFilter(
                filter_field="primary_category__translations__name", placeholder=_("Filter by location name...")
            ),
        ),
        Column(
            "progress",
            _("Goal Progress"),
            display="format_goal_progress",
            ordering=8,
            raw=True,
        ),
        Column(
            "ordering",
            _("Order of appearance"),
            display="get_ordering_field",
            ordering=14,
            sortable=False,
            raw=True,
        ),
        Column(
            "primary",
            _("Set as Primary"),
            display="get_primary_button",
            ordering=15,
            sortable=False,
            linked=True,
            raw=True,
        ),
        Column(
            "promoting",
            _("Promote"),
            display="get_promote_button",
            ordering=20,
            sortable=False,
            linked=True,
            raw=True,
        ),
    ]

    def get_queryset(self):
        shop = get_shop(self.request)
        qs = ShopProduct.objects.filter(shop=shop, suppliers__deleted=False, product__mode=ProductMode.NORMAL)
        qs = filter_approved_shop_products(qs)
        if not givesome_promote_invisible(shop):
            qs = qs.filter(visibility__in=[ShopProductVisibility.ALWAYS_VISIBLE, ShopProductVisibility.ONLY_VISIBLE_WHEN_PROMOTED])
        return qs.exclude(
            Q(product__deleted=True)
            | Q(product__project_extra__isnull=True)
            | Q(product__project_extra__fully_funded_date__isnull=False)
            | Q(product__type__isnull=True)
        )

    def get_object_url(self, instance):
        return None  # No edit for promoted products

    def get_name(self, instance):
        name = instance.product.safe_translation_getter("name")
        front_url = reverse("shuup:product", kwargs={"pk": instance.product.pk, "slug": instance.product.slug})
        if instance.visibility is not ShopProductVisibility.NOT_VISIBLE:
            return f'<a href="{front_url}">{name}</a>'
        return f"{name}"

    def get_description(self, instance):
        return instance.product.safe_translation_getter("short_description")

    def get_supplier_name(self, instance):
        return instance.suppliers.first().name

    def format_goal_progress(self, instance):
        if hasattr(instance.product, "project_extra"):
            goal = instance.product.project_extra.goal_amount
            current = instance.product.project_extra.goal_progress_amount
            percentage = instance.product.project_extra.goal_progress_percentage
            date = instance.product.project_extra.fully_funded_date
            if date is not None:
                date = f'<br>Fully funded on: {date.strftime("%Y-%m-%d")}'
            else:
                date = ""
            return f"{percentage}%, (${current} / ${goal}){date}"
        return ""

    def get_promote_button(self, instance):
        context = self._get_promote_context(instance)
        return render_to_string("givesome/admin/projects/promote_button.jinja", context=context, request=self.request)

    def get_primary_button(self, instance):
        context = self._get_primary_context(instance)
        if context is None:
            # Hide button if supplier is a charity
            return ""
        return render_to_string("givesome/admin/projects/primary_button.jinja", context=context, request=self.request)

    def get_ordering_field(self, instance):
        context = self._get_primary_context(instance)
        if context is None:
            # Hide button if supplier is a charity
            return ""
        return render_to_string(
            "givesome/admin/projects/order_promoted_projects.jinja", context=context, request=self.request
        )

    def dispatch(self, request, *args, **kwargs):
        return PicotableListView.dispatch(self, request, *args, **kwargs)

    def process_picotable(self, query_json):
        return PicotableListView.process_picotable(self, query_json)

    def get_toolbar(self):
        return []

    def _get_promote_context(self, instance):
        raise NotImplementedError

    def _get_primary_context(self, instance):
        raise NotImplementedError


class OfficeProjectPromoteEditView(ProjectPromoteEditView):
    def get_toolbar(self):
        supplier = get_supplier(self.request)
        offices = GivesomeOffice.objects.all()
        if supplier:
            offices = offices.filter(supplier=supplier)

        menu_items = []
        for office in offices:
            menu_items.append(
                URLActionButton(
                    url=reverse("shuup_admin:office_project_promote.edit", kwargs={"pk": office.pk}),
                    text=office.name,
                    tooltip=_("Manage office promoted projects"),
                    icon="fa fa-circle-o",
                )
            )

        return Toolbar(
            [
                DropdownActionButton(
                    menu_items,
                    icon="fa fa-building-o",
                    text=_("Select Office"),
                    extra_css_class="btn-inverse btn-actions",
                )
            ],
            view=self,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        office_id = self.kwargs.pop("pk", None)
        supplier = get_supplier(self.request)
        offices = GivesomeOffice.objects.filter(pk=office_id)
        if supplier:
            offices = offices.filter(supplier=supplier)
        office = offices.first()
        if office:
            context["title"] = office.name
        else:
            raise Http404()
        return context

    def _get_context_office(self):
        office_id = self.kwargs["pk"]
        supplier = get_supplier(self.request)
        offices = GivesomeOffice.objects.filter(pk=office_id)
        if supplier:
            offices = offices.filter(supplier=supplier)
        office = offices.first()
        assert office is not None
        return office

    def _get_promote_context(self, instance):
        office = self._get_context_office()

        promoting = instance.promotions.filter(office=office).exists()
        if not promoting:
            text = _("Start promoting this product")
        else:
            text = _("Stop promoting this product")

        return {
            "text": text,
            "is_promoting": promoting,
            "instance": instance,
            "chooser_id": office.id,
            "kind": "office",
        }

    def _get_primary_context(self, instance):
        office = self._get_context_office()

        is_primary = office.primary_project == instance
        if office.primary_project is None or not is_primary:
            text = _("Set as primary project")
        else:
            text = _("Remove as primary project")

        return {"text": text, "is_primary": is_primary, "instance": instance, "chooser_id": office.id, "kind": "office"}


class VendorProjectPromoteEditView(ProjectPromoteEditView):
    def get_queryset(self):
        supplier = self._get_context_supplier()
        qs = super().get_queryset()
        # If supplier is a charity, exclude their own projects
        if supplier.givesome_extra.vendor_type == VendorExtraType.CHARITY:
            qs = qs.exclude(suppliers=supplier)
        return qs

    def get_toolbar(self):
        supplier = get_supplier(self.request)
        if supplier:
            return []

        suppliers = Supplier.objects.filter(givesome_extra__vendor_type=VendorExtraType.BRANDED_VENDOR)

        menu_items = []
        for supplier in suppliers:
            menu_items.append(
                URLActionButton(
                    url=reverse("shuup_admin:vendor_project_promote.edit", kwargs={"pk": supplier.pk}),
                    text=supplier.name,
                    tooltip=_("Manage vendor promoted projects"),
                    icon="fa fa-circle-o",
                )
            )

        return Toolbar(
            [
                DropdownActionButton(
                    menu_items,
                    icon="fa fa-building-o",
                    text=_("Select Vendor"),
                    extra_css_class="btn-inverse btn-actions",
                )
            ],
            view=self,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = get_supplier(self.request)
        supplier_id = self.kwargs.pop("pk", None)
        suppliers = Supplier.objects.filter(pk=supplier_id)
        if supplier:
            suppliers = suppliers.filter(pk=supplier.pk)
        supplier = suppliers.first()
        if supplier:
            context["title"] = supplier.name
        else:
            raise Http404()
        return context

    def _get_context_supplier(self):
        supplier_id = self.kwargs["pk"]
        supplier = get_supplier(self.request)
        suppliers = Supplier.objects.filter(pk=supplier_id)
        if supplier:
            suppliers = suppliers.filter(pk=supplier.id)
        supplier = suppliers.first()
        assert supplier is not None
        return supplier

    def _get_promote_context(self, instance):
        supplier = self._get_context_supplier()

        promoting = instance.promotions.filter(supplier=supplier).exists()
        if not promoting:
            text = _("Start promoting this product")
        else:
            text = _("Stop promoting this product")

        return {
            "text": text,
            "is_promoting": promoting,
            "instance": instance,
            "chooser_id": supplier.id,
            "kind": "vendor",
        }

    def _get_primary_context(self, instance):
        supplier = self._get_context_supplier()

        if supplier.givesome_extra.vendor_type == VendorExtraType.CHARITY:
            # Button not available for charities
            return None

        is_primary = supplier.givesome_extra.primary_project == instance
        if supplier.givesome_extra.primary_project is None or not is_primary:
            text = _("Set as primary project")
        else:
            text = _("Remove as primary project")

        return {
            "text": text,
            "is_primary": is_primary,
            "instance": instance,
            "chooser_id": supplier.id,
            "kind": "vendor",
        }


class OfficePostView(View):
    def __init__(self):
        super().__init__()
        self.supplier = None
        self.office = None
        self.project = None

    def post(self, request, *args, **kwargs):
        self.supplier = get_supplier(self.request)

        offices = GivesomeOffice.objects.filter(pk=int(request.POST.get("chooserId")))
        if self.supplier:
            offices = offices.filter(supplier=self.supplier)

        self.office = offices.first()
        if self.office is None:
            raise Http404()

        self.project = ShopProduct.objects.filter(pk=int(request.POST.get("productId"))).first()
        if self.project is None:
            raise Http404()


class OfficeTogglePromoteView(OfficePostView):
    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        office = self.office
        project = self.project

        is_promoting = False
        if GivesomePromotedProduct.objects.filter(office=office, shop_product=project).exists():
            GivesomePromotedProduct.objects.filter(office=office, shop_product=project).delete()
        else:
            is_promoting = True
            GivesomePromotedProduct.objects.create(office=office, shop_product=project)

        bump_product_queryset_cache()

        if request.is_ajax():
            return JsonResponse({"is_promoting": is_promoting})


class OfficeSetPrimaryView(OfficePostView):
    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        office = self.office
        project = self.project

        is_primary = False
        if office.primary_project == project:
            office.primary_project = None
        else:
            office.primary_project = project
            is_primary = True
        office.save()

        if request.is_ajax():
            return JsonResponse({"is_primary": is_primary})


class VendorPostView(View):
    def __init__(self):
        super().__init__()
        self.supplier = None
        self.project = None

    def post(self, request, *args, **kwargs):
        supplier = get_supplier(self.request)

        suppliers = Supplier.objects.filter(pk=int(request.POST.get("chooserId")))
        if self.supplier:
            suppliers = suppliers.filter(pk=supplier)
        self.supplier = suppliers.first()

        if self.supplier is None:
            raise Http404()

        self.project = ShopProduct.objects.filter(pk=int(request.POST.get("productId"))).first()
        if self.project is None:
            raise Http404()


class VendorTogglePromoteView(VendorPostView):
    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        supplier = self.supplier
        project = self.project

        is_promoting = False
        if GivesomePromotedProduct.objects.filter(supplier=supplier, shop_product=project).exists():
            GivesomePromotedProduct.objects.filter(supplier=supplier, shop_product=project).delete()
        else:
            is_promoting = True
            GivesomePromotedProduct.objects.create(supplier=supplier, shop_product=project)

        bump_product_queryset_cache()

        if request.is_ajax():
            return JsonResponse({"is_promoting": is_promoting})


class VendorSetPrimaryView(VendorPostView):
    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        supplier = self.supplier
        project = self.project

        is_primary = False
        if supplier.givesome_extra.primary_project == project:
            supplier.givesome_extra.primary_project = None
        else:
            supplier.givesome_extra.primary_project = project
            is_primary = True
        supplier.givesome_extra.save()

        if request.is_ajax():
            return JsonResponse({"is_primary": is_primary})


class OrderPromotedProjectsView(View):
    def post(self, request, *args, **kwargs):
        supplier = get_supplier(request)
        promoted_product_qs = GivesomePromotedProduct.objects.filter(shop_product_id=kwargs["shop_product_id"])
        staff_user = supplier is None and self.request.user.is_staff
        if kwargs["type"] == "vendor":
            if not staff_user and supplier.id != int(kwargs["promoter_id"]):
                # Allowed: staff users and the vendor itself.
                return JsonResponse({"status": "failed"}, status=403)
            promoted_project_qs = promoted_product_qs.filter(supplier_id=kwargs["promoter_id"])
        else:
            if not staff_user and int(kwargs["promoter_id"]) not in supplier.offices.all().values_list("id", flat=True):
                # Allowed: staff users and the vendor itself.
                return JsonResponse({"status": "failed"}, status=403)
            promoted_project_qs = promoted_product_qs.filter(office_id=kwargs["promoter_id"])

        reordered = promoted_project_qs.update(ordering=request.POST.get("position"))
        if reordered == 1:
            return JsonResponse({"promotedProjectId": promoted_project_qs.first().id, "status": "updated"})
        else:
            return JsonResponse({"status": "failed"}, status=404)

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from parler.utils import get_active_language_choices
from shuup.core.models import Category, CategoryStatus, Product, ShopProductVisibility
from shuup.front.forms.product_list_modifiers import CommaSeparatedListField
from shuup_multivendor.views import SupplierList
from shuup_multivendor.views.vendor import SupplierView

from givesome.admin_module.forms.shop_settings import givesome_fully_funded_display_days
from givesome.enums import VendorExtraType
from givesome.front.utils import filter_valid_projects
from givesome.models import GivesomeOffice, SustainabilityGoal


class GivesomeSupplierList(SupplierList):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(givesome_extra__isnull=False, givesome_extra__allow_brand_page=True)
            .order_by("-givesome_extra__ordering")
        )


class GivesomeCharityList(GivesomeSupplierList):
    def get_queryset(self):
        return super().get_queryset().filter(givesome_extra__vendor_type=VendorExtraType.CHARITY)


class GivesomeBrandedList(GivesomeSupplierList):
    def get_queryset(self):
        return super().get_queryset().filter(givesome_extra__vendor_type=VendorExtraType.BRANDED_VENDOR)


class GivesomeBaseBrandView(SupplierView):
    """Not used directly. Inherited by Supplier and Office views"""

    def _get_sustainability_goals(self):
        if hasattr(self.object, "vendor_sustainability_goals"):
            return self.object.vendor_sustainability_goals.goals.all()
        return []

    def _get_filter_category_ids(self):
        raise NotImplementedError

    def _custom_product_filter(self, qs):
        raise NotImplementedError

    def _build_categories_filter(self):
        # Only categories that are in promoted products are choices in the filter
        category_ids = self._get_filter_category_ids()
        queryset = (
            Category.objects.active_translations(get_language())
            .filter(pk__in=category_ids)
            .distinct()
            .values_list("pk", "translations__name")
        )
        choices = [(identifier, name) for identifier, name in queryset]
        if choices:
            return CommaSeparatedListField(
                required=False, label=_("Location"), widget=forms.SelectMultiple(choices=choices)
            )
        return False

    def _build_sdgs_filter(self):
        qs = SustainabilityGoal.objects.active_translations(get_language()).values_list("pk", "translations__name")
        choices = [(identifier, name) for identifier, name in qs]
        if choices:
            return CommaSeparatedListField(
                required=False, label=_("Sustainable Development Goals"), widget=forms.SelectMultiple(choices=choices)
            )
        return False

    def _get_base_products_qs(self, data, catalog):
        # Projects completed before this date are not shown
        fully_funded_cutoff_date = timezone.now() - timezone.timedelta(
            days=givesome_fully_funded_display_days(shop=self.request.shop)
        )

        products = (
            catalog.annotate_products_queryset(Product.objects.all(), annotate_discounts=False)
            .filter(
                shop_products__shop=self.request.shop,
                shop_products__visibility__in=[ShopProductVisibility.ALWAYS_VISIBLE, ShopProductVisibility.ONLY_VISIBLE_WHEN_PROMOTED],
                variation_parent__isnull=True,
            )
            .exclude(project_extra__isnull=True)
            .exclude(
                Q(project_extra__fully_funded_date__isnull=False)
                & Q(project_extra__fully_funded_date__lte=fully_funded_cutoff_date)
            )
            .distinct()
        )
        products = filter_valid_projects(products, promoted=True)

        # Apply form filters and sorts
        return products

    def _get_context_products(self, supplier, data):
        from shuup.core.catalog import ProductCatalog, ProductCatalogContext

        catalog = ProductCatalog(
            ProductCatalogContext(
                shop=self.request.shop,
                user=getattr(self.request, "user", None),
                contact=getattr(self.request, "customer", None),
                supplier=supplier,
            )
        )
        products = self._get_base_products_qs(data, catalog)
        products = self._custom_product_filter(products).distinct()
        products = products.order_by("shop_products__promotions__ordering")
        return products

    def get_context_data(self, **kwargs):
        # Use DetailView instead of super `get_context_data` to not do the same thing twice
        context = DetailView.get_context_data(self, **kwargs)
        context["supplier"] = self.object

        data = self.request.GET
        from shuup.front.utils.sorts_and_filters import ProductListForm

        context["form"] = form = ProductListForm(request=self.request, shop=self.request.shop, category=None, data=data)
        form.full_clean()
        data = form.cleaned_data
        data["supplier"] = self.object

        # Category filter
        categories_filter = self._build_categories_filter()
        if categories_filter:
            form.fields["categories"] = categories_filter

        # Sustainability Goal filter
        sdgs_filter = self._build_sdgs_filter()
        if sdgs_filter:
            form.fields["sustainability_goals"] = sdgs_filter

        # Sort
        if "sort" in form.fields and not data.get("sort"):
            # Use first choice by default
            data["sort"] = form.fields["sort"].widget.choices[0][0]

        # Products
        supplier = self.object or None
        if isinstance(self.object, GivesomeOffice):
            supplier = self.object.supplier

        products = self._get_context_products(supplier, data)

        language = get_active_language_choices()[0]
        for product in products:
            product.set_current_language(language)
        context["products"] = products

        context["sustainability_goals"] = self._get_sustainability_goals()

        return context


class GivesomeSupplierView(GivesomeBaseBrandView):
    def get_queryset(self):
        if 'slug' in self.kwargs:
            self.kwargs['slug'] = self.kwargs['slug'].lower()
        return super().get_queryset().filter(givesome_extra__allow_brand_page=True)

    def _is_charity(self):
        return self.object.givesome_extra.vendor_type == VendorExtraType.CHARITY

    def _get_filter_category_ids(self):
        if self._is_charity():
            return (
                self.object.shop_products.filter(
                    shop=self.request.shop,
                    primary_category__isnull=False,
                    primary_category__status=CategoryStatus.VISIBLE,
                    product__deleted=False,
                    visibility=ShopProductVisibility.ALWAYS_VISIBLE,
                )
                .values_list("primary_category")
                .distinct()
            )
        return (
            self.object.promoted_projects.filter(
                shop_product__shop=self.request.shop,
                shop_product__primary_category__isnull=False,
                shop_product__primary_category__status=CategoryStatus.VISIBLE,
                shop_product__product__deleted=False,
                shop_product__visibility=ShopProductVisibility.ALWAYS_VISIBLE,
            )
            .values_list("shop_product__primary_category")
            .distinct()
        )

    def _custom_product_filter(self, qs):
        """
        Return projects promoted by the supplier
        For charities also return all of their own projects
        """
        filters = Q(shop_products__promotions__supplier=self.object)
        if self._is_charity():
            filters |= Q(shop_products__suppliers=self.object, shop_products__visibility=ShopProductVisibility.ALWAYS_VISIBLE)
        return qs.filter(filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object and hasattr(self.object, "givesome_extra"):
            extra = self.object.givesome_extra
            if extra is not None and extra.sponsored_by is not None:
                context["sponsoring_vendor"] = extra.sponsored_by

        context["promoter"] = self.object
        if not self._is_charity():
            context["brand"] = self.object
            context["offices"] = self.object.offices.filter(level=0, disabled=False).order_by("ordering")
            context["office_term"] = self.object.office_terms.filter(level=0).first()
        return context

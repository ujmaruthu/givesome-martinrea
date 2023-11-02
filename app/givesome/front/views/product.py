# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import Product, ProductMode, ShopProduct, Supplier
from shuup.front.views.product import ProductDetailView
from shuup.utils.django_compat import reverse
from shuup.utils.excs import Problem, extract_messages

from givesome.front.receipting_checkout_state import wants_receipt, within_time
from givesome.front.utils import filter_valid_projects, get_promoter_from_request, get_shop_product_visibility_errors
from givesome.models import GivesomeOffice


class GivesomeProjectDetailView(ProductDetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        promoter, promoter_type = get_promoter_from_request(self.request)
        context["promoter_type"] = promoter_type
        context["promoter"] = promoter
        context["subscription"] = self.object.mode == ProductMode.SUBSCRIPTION
        subscription = context["supplier"].shop_products.filter(product__mode=ProductMode.SUBSCRIPTION).first()
        context["charity_subscription_product"] = subscription.product if subscription is not None else subscription

        projects = Product.objects.exclude(id=self.object.id)
        projects = filter_valid_projects(projects).filter(project_extra__fully_funded_date__isnull=True)

        if isinstance(promoter, GivesomeOffice):
            context["brand"] = promoter.supplier
            context["promoted_projects"] = projects.filter(shop_products__promotions__office=promoter)
        elif isinstance(promoter, Supplier):
            context["brand"] = promoter
            context["promoted_projects"] = projects.filter(shop_products__promotions__supplier=promoter)
        else:
            supplier = context.get("supplier")
            context["brand"] = None
            context["supplier_projects"] = projects.filter(shop_products__suppliers=supplier)
            if supplier is not None:
                context["charity_allow_brand_page"] = supplier.givesome_extra.allow_brand_page

        if context.get("brand") and not context["brand"].givesome_extra.show_promoted:
            context["promoted_projects"] = []

        context["wants_receipt"] = str(wants_receipt(self.request)).lower()
        receipting_wishes = self.request.session.get("requesting_receipt")
        if receipting_wishes is None:
            context["mid_receipting_process"] = "false"
        else:
            context["mid_receipting_process"] = str(within_time(self.request)).lower()

        extra = self.object.project_extra
        if extra is not None and extra.sponsored_by is not None:
            context["sponsoring_vendor"] = extra.sponsored_by
        if extra is not None and extra.donation_url is not None:
            context["donation_url"] = extra.donation_url
        return context

    def get(self, request, *args, **kwargs):
        """Override `get` method to modify shop_product `get_visibility_errors`"""
        product = self.object = self.get_object()

        if product.mode == ProductMode.VARIATION_CHILD:
            # redirect to parent url with child pre-selected
            parent_url = reverse(
                "shuup:product", kwargs=dict(pk=product.variation_parent.pk, slug=product.variation_parent.slug)
            )
            return HttpResponseRedirect("{}?variation={}".format(parent_url, product.sku))

        try:
            shop_product = self.shop_product = product.get_shop_instance(request.shop, allow_cache=True)
        except ShopProduct.DoesNotExist:
            raise Problem(_(u"Error! This product is not available in this shop."))

        errors = list(get_shop_product_visibility_errors(shop_product, customer=request.customer))

        if errors:
            raise Problem("\n".join(extract_messages(errors)))

        return super(ProductDetailView, self).get(request, *args, **kwargs)

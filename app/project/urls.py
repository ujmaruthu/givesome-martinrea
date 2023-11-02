# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, path
from django.views.decorators.csrf import csrf_exempt
from shuup.admin.modules.products.views import ProductMediaBulkAdderView
from shuup.admin.views.dashboard import DashboardView
from shuup.core.utils.maintenance import maintenance_mode_exempt

from givesome.admin_module.views.givecard_batch import GivecardBatchDownloadView, nullify_batch
from givesome.admin_module.views.progress_management import GivesomeProcessStockFormView
from givesome.front.views import GivesomeBrandedList, GivesomeCharityList, GivesomeSupplierView
from givesome.front.views.givecard_redeem import GivecardRedeemView
from givesome.front.views.givecard_wallet import GivecardWalletView
from givesome.front.views.office import GivesomeOfficeView
from givesome.front.views.product import GivesomeProjectDetailView
from givesome.front.views.profile import (
    OffPlatformCreateView,
    OffPlatformDeleteView,
    OffPlatformListView,
    OffPlatformUpdateView,
)
from givesome.front.views.receipting_customer_edit import GivesomeCustomerEditView


def not_vendor(view):
    def f(request, *args, **kwargs):
        user = request.user
        is_anonymous = getattr(user, "is_anonymous", False)
        is_superuser = getattr(user, "is_superuser", False)
        is_staff_member = request.shop and request.shop.staff_members.filter(id=user.id).exists()
        if is_anonymous or is_superuser or is_staff_member:
            return login_required(view, login_url="shuup_admin:login")(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("shuup_admin:shuup_multivendor.dashboard.supplier"))

    return f


urlpatterns = [
    url(r"^api/", include("shuup_api.urls")),
    url(r"^sa/products/(?P<pk>\d+)/media/add/$", ProductMediaBulkAdderView.as_view(), name="shop_product.add_media_sa"),
    url(r"^admin/$", maintenance_mode_exempt(not_vendor(DashboardView.as_view())), name="dashboard"),
    url(r"^admin/", include("shuup.admin.urls", namespace="shuup_admin")),
    # Override firebase customer edit view
    url(r"^customer/$", GivesomeCustomerEditView.as_view(), name="customer_edit"),
    url(r"^", include("shuup_firebase_auth.auth_urls", namespace="shuup_firebase_auth")),
    url(r"^login/$", lambda request: redirect("shuup_firebase_auth:auth", permanent=True)),
    url(r"^register/$", lambda request: redirect("shuup_firebase_auth:auth", permanent=True)),
    url(r"^recover-password/$", lambda request: redirect("shuup_firebase_auth:reset-password", permanent=True)),
    url(r"^b/$", GivesomeBrandedList.as_view(), name="branded_vendor_list"),
    url(r"^v/$", GivesomeCharityList.as_view(), name="supplier_list"),
    url(r"^v/(?P<pk>\d+)/$", GivesomeSupplierView.as_view(), name="supplier"),
    url(r"^v/(?P<pk>\d+)-(?P<slug>[^/]+)/$", GivesomeSupplierView.as_view(), name="supplier"),
    url(r"^o/(?P<pk>\d+)/$", GivesomeOfficeView.as_view(), name="office"),
    url(r"^o/(?P<pk>\d+)-(?P<slug>[^/]+)/$", GivesomeOfficeView.as_view(), name="office"),
    url(r"^redeem/$", GivecardRedeemView.as_view(), name="givecard_redeem"),
    url(r"^wallet/$", GivecardWalletView.as_view(), name="givecard_wallet"),
    url(
        r"^adjust-progress/(?P<supplier_id>\d+)/(?P<project_id>\d+)/",
        GivesomeProcessStockFormView.as_view(),
        name="adjust-progress",
    ),
    url(r"download-batch/(?P<pk>\d+)/", GivecardBatchDownloadView.as_view(), name="download-batch"),
    url(r"nullify-batch/(?P<pk>\d+)/", nullify_batch, name="nullify-batch"),
    url(r"create-off-platform/(?P<type>[A-Za-z]+)/$", OffPlatformCreateView.as_view(), name="create-off-platform"),
    url(
        r"update-off-platform/(?P<type>[A-Za-z]+)/(?P<pk>\d+)/$",
        OffPlatformUpdateView.as_view(),
        name="update-off-platform",
    ),
    url(
        r"delete-off-platform/(?P<type>[A-Za-z]+)/(?P<pk>\d+)/$",
        OffPlatformDeleteView.as_view(),
        name="delete-off-platform",
    ),
    url(r"load-off-platform/(?P<type>[A-Za-z]+)/$", OffPlatformListView.as_view(), name="load-off-platform"),
    url(r"^p/(?P<pk>\d+)-(?P<slug>.*)/$", csrf_exempt(GivesomeProjectDetailView.as_view()), name="product"),
    url(r"^", include("shuup.front.urls", namespace="shuup")),
]


if settings.DEBUG:
    # urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

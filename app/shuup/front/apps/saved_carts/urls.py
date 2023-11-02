# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r"^saved-carts/$", login_required(views.CartListView.as_view()), name="saved_cart.list"),
    url(r"^saved-carts/save/$", login_required(views.CartSaveView.as_view()), name="saved_cart.save"),
    url(
        r"^saved-carts/(?P<pk>\d+)/add/$",
        login_required(views.CartAddAllProductsView.as_view()),
        name="saved_cart.add_all",
    ),
    url(r"^saved-carts/(?P<pk>\d+)/delete/$", login_required(views.CartDeleteView.as_view()), name="saved_cart.delete"),
    url(r"^saved-carts/(?P<pk>.+)/$", login_required(views.CartDetailView.as_view()), name="saved_cart.detail"),
]

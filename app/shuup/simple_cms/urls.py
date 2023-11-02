# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.conf.urls import url

from shuup.simple_cms.views import PageView

urlpatterns = [
    url(r"^(?P<url>.*)/$", PageView.as_view(), name="cms_page"),
]

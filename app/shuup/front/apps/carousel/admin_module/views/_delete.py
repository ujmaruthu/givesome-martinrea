# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from shuup.admin.utils.urls import get_model_url
from shuup.front.apps.carousel.models import Carousel
from shuup.utils.django_compat import reverse


class CarouselDeleteView(DetailView):
    model = Carousel
    context_object_name = "carousel"

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(get_model_url(self.get_object()))

    def post(self, request, *args, **kwargs):
        carousel = self.get_object()
        name = carousel.name
        carousel.delete()
        messages.success(request, _("%s has been deleted.") % name)
        return HttpResponseRedirect(reverse("shuup_admin:carousel.list"))

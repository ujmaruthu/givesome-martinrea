# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.http.response import JsonResponse
from django.views.generic import View

from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.tour import set_tour_complete


class TourView(View):
    def post(self, request, *args, **kwargs):
        tour_key = request.POST.get("tourKey", "")
        set_tour_complete(get_shop(request), tour_key, True, request.user)
        return JsonResponse({"success": True})

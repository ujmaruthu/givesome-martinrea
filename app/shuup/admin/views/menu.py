# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.http import JsonResponse
from django.views.generic import TemplateView, View


class MenuView(TemplateView):
    template_name = "shuup/admin/base/_main_menu.jinja"


class MenuToggleView(View):
    def post(self, request, *args, **kwargs):
        request.session["menu_open"] = not bool(request.session.get("menu_open", True))
        return JsonResponse({"success": True})

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.http import JsonResponse
from django.views import View


class SetTimezoneView(View):
    """This view is called by a script in base.jinja to set the session's timezone."""

    def post(self, request):
        request.session["tz"] = request.POST["name"]
        return JsonResponse({})

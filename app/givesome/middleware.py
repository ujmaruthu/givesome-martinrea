# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import pytz
from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from shuup.core.models import get_person_contact


class ActivateTimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        person = get_person_contact(request.user)

        if person.timezone:
            tz = person.timezone
        elif request.session.get("tz"):
            tz = pytz.timezone(request.session["tz"])
        else:
            tz = settings.TIME_ZONE

        timezone.activate(tz)

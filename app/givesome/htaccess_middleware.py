# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from base64 import b64encode

from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import ugettext as _


def basic_challenge(realm=None):
    if realm is None:
        realm = getattr(settings, "WWW_AUTHENTICATION_REALM", _("Restricted Access"))
    response = HttpResponse(_("Authorization Required"))
    response["WWW-Authenticate"] = 'Basic realm="%s"' % (realm)
    response.status_code = 401
    return response


def basic_authenticate(authentication):
    # Taken from paste.auth
    (authmeth, auth) = authentication.split(" ", 1)
    if "basic" != authmeth.lower():
        return None

    auth_username = getattr(settings, "BASIC_WWW_AUTHENTICATION_USERNAME")
    auth_password = getattr(settings, "BASIC_WWW_AUTHENTICATION_PASSWORD")
    auth_str = "%s:%s" % (auth_username, auth_password)
    return auth.strip() == b64encode(bytes(auth_str, encoding="utf-8")).decode("ascii")


class BasicAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not getattr(settings, "BASIC_WWW_AUTHENTICATION", False):
            return
        if "HTTP_AUTHORIZATION" not in request.META:
            return basic_challenge()
        authenticated = basic_authenticate(request.META["HTTP_AUTHORIZATION"])
        if authenticated:
            return
        return basic_challenge()

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib.auth.models import AnonymousUser


def _is_admin_user(request):
    user = getattr(request, "user", AnonymousUser())
    shop = getattr(request, "shop", None)
    if not (user and shop):
        return False

    if getattr(user, "is_superuser", False):
        return True

    return bool(getattr(user, "is_staff", False) and shop.staff_members.filter(id=user.id).exists())


def is_admin_user(request):
    if getattr(request, "is_admin_user", False):
        return True
    setattr(request, "is_admin_user", _is_admin_user(request))
    return getattr(request, "is_admin_user", False)

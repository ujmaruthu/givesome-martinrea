# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.core.models import Supplier


class UsernameSupplierProvider(object):
    @classmethod
    def get_supplier(cls, request, **kwargs):
        return Supplier.objects.filter(identifier=request.user.username).first()


class RequestSupplierProvider(object):
    @classmethod
    def get_supplier(cls, request, **kwargs):
        return getattr(request, "supplier", None)


class FirstSupplierProvider(object):
    @classmethod
    def get_supplier(cls, request, **kwargs):
        return Supplier.objects.first()

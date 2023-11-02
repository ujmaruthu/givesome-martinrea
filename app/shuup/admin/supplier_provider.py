# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.utils.importing import cached_load


class DefaultSupplierProvider(object):
    @classmethod
    def get_supplier(cls, request, **kwargs):
        return None


def get_supplier(request, **kwargs):
    return cached_load("SHUUP_ADMIN_SUPPLIER_PROVIDER_SPEC").get_supplier(request, **kwargs)

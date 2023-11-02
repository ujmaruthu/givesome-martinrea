# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from shuup.core.models import ProductPackageLink


def clear_existing_package(parent_product):
    """
    Utility function for clearing existing package.
    """
    children = parent_product.get_package_child_to_quantity_map().keys()
    ProductPackageLink.objects.filter(parent=parent_product).delete()
    parent_product.verify_mode()
    parent_product.save()
    for child in children:
        child.verify_mode()
        child.save()

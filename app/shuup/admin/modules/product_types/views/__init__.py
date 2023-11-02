# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from .delete import ProductTypeDeleteView
from .edit import ProductTypeEditView
from .list import ProductTypeListView

__all__ = ["ProductTypeEditView", "ProductTypeListView", "ProductTypeDeleteView"]

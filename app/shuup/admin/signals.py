# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.dispatch import Signal

view_form_valid = Signal(providing_args=["form", "view", "request"], use_caching=True)
object_created = Signal(providing_args=["object", "request"], use_caching=True)
object_saved = Signal(providing_args=["object", "request"], use_caching=True)
form_post_clean = Signal(providing_args=["instance", "cleaned_data"], use_caching=True)
form_pre_clean = Signal(providing_args=["instance", "cleaned_data"], use_caching=True)
product_copied = Signal(providing_args=["shop", "supplier", "copied", "copy"], use_caching=True)

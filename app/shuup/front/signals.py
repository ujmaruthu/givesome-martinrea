# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.signals import Signal

# Modifying signals
from shuup.core.signals import get_basket_command_handler  # noqa

# Completion signals
order_complete_viewed = Signal(providing_args=["order", "request"], use_caching=True)


checkout_complete = Signal(providing_args=["request", "user", "order"], use_caching=True)
login_allowed = Signal(providing_args=["request", "user"], use_caching=True)
person_registration_save = Signal(providing_args=["request", "user", "contact"], use_caching=True)
company_registration_save = Signal(providing_args=["request", "user", "company"], use_caching=True)

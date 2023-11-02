# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

import six
from django.contrib import messages

from shuup.core.basket.update_methods import BasketUpdateMethods as CoreBasketUpdateMethods


class BasketUpdateMethods(CoreBasketUpdateMethods):
    def _handle_orderability_error(self, line, error):
        error_texts = ", ".join(six.text_type(sub_error) for sub_error in error)
        message = "Warning! %s: %s" % (line.get("text") or line.get("name"), error_texts)
        messages.warning(self.request, message)

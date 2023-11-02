# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.dispatch import receiver

from shuup.core.signals import shuup_initialized
from shuup.reports.constants import DEFAULT_REPORTS_ITEM_LIMIT
from shuup.reports.setting_keys import SHUUP_DEFAULT_REPORTS_ITEM_LIMIT


@receiver(shuup_initialized)
def on_shuup_initialized(sender, **kwargs):
    from shuup import configuration

    configuration.set(None, SHUUP_DEFAULT_REPORTS_ITEM_LIMIT, DEFAULT_REPORTS_ITEM_LIMIT)

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup.core.setting_keys import SHUUP_LENGTH_UNIT


def get_shuup_volume_unit():
    """
    Return the volume unit that Shuup should use.

    :rtype: str
    """
    from shuup import configuration

    return "{}3".format(configuration.get(None, SHUUP_LENGTH_UNIT))

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.


def maintenance_mode_exempt(view_func):
    """
    Make view ignore shop maintenance mode

    :param view_func: view attached to this decorator
    :return: view added with maintenance_mode_exempt attribute
    """
    view_func.maintenance_mode_exempt = True
    return view_func

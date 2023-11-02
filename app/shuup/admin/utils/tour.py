# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from shuup import configuration


def is_tour_complete(shop, tour_key, user=None):
    """
    Check if the tour is complete

    :param tour_key: The tour key.
    :type field: str
    :return: whether tour is complete
    :rtype: Boolean
    """
    user_id = user.pk if user else "-"
    return configuration.get(shop, "shuup_%s_%s_tour_complete" % (tour_key, user_id), False)


def set_tour_complete(shop, tour_key, complete=True, user=None):
    user_id = user.pk if user else "-"
    return configuration.set(shop, "shuup_%s_%s_tour_complete" % (tour_key, user_id), complete)

# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.signals import Signal

post_compute_source_lines = Signal(providing_args=["source", "lines"], use_caching=True)
order_creator_finished = Signal(providing_args=["order", "source"], use_caching=True)
post_order_line_save = Signal(providing_args=["order_line", "order"], use_caching=True)

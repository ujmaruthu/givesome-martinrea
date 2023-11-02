# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

MESSAGE_SUBJECT_TEMPLATE = "{{ order.shop }} - Order {{ order.identifier }} Received"
MESSAGE_BODY_TEMPLATE = """
Thank you for your order, {{ order.customer }}!

Your order has been received and will be processed as soon as possible.

For reference, here's a list of your order's contents.

{% for line in order.lines.all() %}
* {{ line.quantity }} x {{ line.text }} - {{ line.taxful_price|money }}
{%- endfor %}

Order Total: {{ order.taxful_total_price|money }}

{% if not order.is_paid() %}
Please note that no record of your order being paid currently exists.
{% endif %}

Thank you for shopping with us!
""".strip()

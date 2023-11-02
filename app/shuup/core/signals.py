# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.dispatch import Signal

shuup_initialized = Signal(providing_args=["shop"], use_caching=True)
get_visibility_errors = Signal(providing_args=["shop_product", "customer"], use_caching=True)
get_orderability_errors = Signal(providing_args=["shop_product", "customer", "supplier", "quantity"], use_caching=True)
shipment_created = Signal(providing_args=["order", "shipment"], use_caching=True)
shipment_created_and_processed = Signal(providing_args=["order", "shipment"], use_caching=True)
shipment_sent = Signal(providing_args=["order", "shipment"], use_caching=True)
refund_created = Signal(providing_args=["order", "refund_lines"], use_caching=True)
category_deleted = Signal(providing_args=["category"], use_caching=True)
shipment_deleted = Signal(providing_args=["shipment"], use_caching=True)
payment_created = Signal(providing_args=["order", "payment"], use_caching=True)
get_basket_command_handler = Signal(providing_args=["command"], use_caching=True)
pre_clean = Signal(providing_args=["instance"], use_caching=True)
post_clean = Signal(providing_args=["instance"], use_caching=True)
context_cache_item_bumped = Signal(providing_args=["item", "shop_id"], use_caching=True)
order_changed = Signal(providing_args=["order"], use_caching=True)
order_status_changed = Signal(providing_args=["order", "old_status", "new_status"], use_caching=True)
user_reset_password_requested = Signal(providing_args=["shop", "user", "reset_domain_url", "reset_url_name"])
settings_updated = Signal(providing_args=["shop"], use_caching=True)

#: Sent from supplier module after the stocks updated have
#: been triggered after order, shipment and shop product change.
#:
#: For example:
#:      You can attach signal receiver for this to change
#:      product visibility after it has become unorderable.
#:
stocks_updated = Signal(providing_args=["shops", "product_ids", "supplier"], use_caching=True)

#: Sent from the `shuup_deployed` management command
shuup_deployed = Signal(use_caching=True)

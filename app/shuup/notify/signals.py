# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.dispatch import Signal

notification_email_before_send = Signal(providing_args=["action", "message", "context"])
notification_email_sent = Signal(providing_args=["message", "context", "smtp_account"])

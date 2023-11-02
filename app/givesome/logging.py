# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import logging

from django.db import models
from django.utils.encoding import force_text
from shuup.notify.models import Script
from shuup.utils.analog import LogEntryKind

from .signals import notification_sent

LOGGER = logging.getLogger(__name__)


def convert_string(obj):
    if isinstance(obj, bool):
        return str(obj).lower()
    if isinstance(obj, (list, tuple)):
        return [convert_string(item) for item in obj]
    if isinstance(obj, dict):
        return {convert_string(key): convert_string(value) for key, value in obj.items()}
    if isinstance(obj, models.Model):
        return convert_string({"model": "{}.{}".format(obj._meta.app_label, obj._meta.model.__name__), "id": obj.pk})
    return force_text(obj)


def log_notification_sent(script, event, shop, **kargs):
    try:
        script.add_log_entry(
            "Script %s exectuted." % script.name,
            user=None,
            identifier="notification_sent",
            kind=LogEntryKind.EDIT,
            extra=dict(event=event.identifier, values=convert_string(event.variable_values)),
        )
    except Exception:
        LOGGER.exception("Failed to log notification changes")


notification_sent.connect(log_notification_sent, sender=Script, dispatch_uid="log_notification_sent")

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField


class PersistentCacheEntry(models.Model):
    module = models.CharField(max_length=64, verbose_name=_("module"))
    key = models.CharField(max_length=64, verbose_name=_("key"))
    time = models.DateTimeField(auto_now=True, verbose_name=_("time"))
    data = JSONField(verbose_name=_("data"))

    class Meta:
        verbose_name = _("cache entry")
        verbose_name_plural = _("cache entries")
        unique_together = (("module", "key"),)

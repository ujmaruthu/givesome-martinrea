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
from parler.models import TranslatedFields
from shuup.core.models import TranslatableShuupModel


class CompletionVideo(TranslatableShuupModel):
    project = models.ForeignKey("shuup.Product", related_name="completion_videos", on_delete=models.PROTECT)
    url = models.CharField(max_length=120, help_text=_("Paste a link to a YouTube video."))
    linked_on = models.DateTimeField(auto_now=True)

    translations = TranslatedFields(
        description=models.TextField(
            blank=True,
            null=True,
            max_length=500,
            verbose_name=_("Description"),
            default="",
        ),
    )

    @property
    def video_id(self):
        return self.url.split("?")[0].split("/")[-1]

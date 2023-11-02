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
from parler.models import TranslatableModel, TranslatedFields
from shuup.core import cache


class ReceiptingMessages(TranslatableModel):
    """Store editable messages to display on hover, where a text plugin won't work well."""

    identifier = "receipting_messages"

    translations = TranslatedFields(
        welcome=models.TextField(default="", help_text=_("Seen by users when they enter the site.")),
        project_card=models.TextField(
            default="", help_text=_("Seen when hovering over the project card receipting symbol.")
        ),
        charity_page=models.TextField(
            default="", help_text=_("Seen when hovering over the charity page receipting symbol.")
        ),
        project_page=models.TextField(
            default="", help_text=_("Seen when hovering over the project page receipting symbol.")
        ),
        checkout_no=models.TextField(default="", help_text=_("When donors do not wish to receive a receipt.")),
        checkout_yes=models.TextField(default="", help_text=_("When donors wish to receive a receipt.")),
        checkout_warn=models.TextField(
            default="", help_text=_("When donors wish to receive a receipt, but have incomplete info.")
        ),
        checkout_givecard=models.TextField(default="", help_text=_("Seen when donating by Givecard.")),
        portfolio=models.TextField(default="", help_text=_("Seen by donors who are editing their profiles.")),
        sign_in_header=models.TextField(
            default="",
            help_text=_("The title seen by an unregistered user if signing up during the receipting process."),
        ),
        sign_in_step_1=models.TextField(
            default="", help_text=_("List the first step the user should follow after logging in.")
        ),
        sign_in_step_2=models.TextField(
            default="", help_text=_("List the second step the user should follow after logging in.")
        ),
        sign_in_step_3=models.TextField(
            default="", help_text=_("List the third step the user should follow after logging in.")
        ),
    )

    def bump_cache(self):
        cache.set(self.identifier, self)

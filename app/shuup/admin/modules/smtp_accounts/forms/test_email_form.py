# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import logging
from django import forms
from django.core.mail.message import EmailMessage
from django.utils.translation import ugettext_lazy as _

LOGGER = logging.getLogger(__name__)


class TestEmailForm(forms.Form):
    recipient = forms.EmailField(
        label=_("Send test email to"),
        required=False,
        widget=forms.EmailInput(attrs=dict(placeholder=_("user@example.com"))),
    )
    send = forms.BooleanField(
        label=_("Send Test Email"), required=False, help_text=_("Check this to send a test email.")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["send"] = False

    def send_test_email(self, recipient, smtp_account):
        subject = _("Hello, {recipient}!").format(recipient=recipient)
        body = _("Hi, {recipient}. This is a test.").format(recipient=recipient)

        with smtp_account.get_connection() as smtp_connection:
            message = EmailMessage(
                subject=subject,
                body=body,
                from_email=smtp_account.default_from_email,
                to=[recipient],
            )
            try:
                num_sent = smtp_connection.send_messages([message])
            except Exception:
                LOGGER.exception("Failed to send a test email")
                return 0

        return num_sent

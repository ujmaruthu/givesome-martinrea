# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import os
import tempfile
from django.conf import settings
from django.core import mail
from django.db import models
from django.db.models import Q
from django.db.models.fields import IntegerField
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum, EnumField
from os import fdopen
from shuup_mirage_field.fields import EncryptedCharField, EncryptedTextField

from ._base import ShuupModel


class SMTPProtocol(Enum):
    NotEncrypted = "none"
    SSL = "ssl"
    TLS = "tls"

    class Labels:
        NotEncrypted = _("Not encrypted")
        SSL = _("SSL")
        TLS = _("TLS")


class SMTPAccount(ShuupModel):
    name = models.CharField(max_length=255, verbose_name=_("Account name"))
    host = models.CharField(max_length=255, verbose_name=_("Host"))
    port = models.IntegerField(verbose_name=_("Port"), default=587)
    default_from_email = models.CharField(
        max_length=250,
        verbose_name=_("Default from email"),
        help_text=_(
            """The default sender's email, e.g. support@store.com or even "Store Support" <support@store.com>"""
        ),
    )
    username = EncryptedCharField(verbose_name=_("Username"))
    password = EncryptedCharField(verbose_name=_("Password"))
    protocol = EnumField(SMTPProtocol, verbose_name=_("Connection protocol"), default=SMTPProtocol.NotEncrypted)
    timeout = IntegerField(
        verbose_name=_("Timeout"),
        default=10,
        help_text=_("Specifies a timeout in seconds for blocking operations like the connection attempt."),
    )
    ssl_certfile = EncryptedTextField(
        verbose_name=_("SSL certificate file"),
        blank=True,
        null=True,
        help_text=_("PEM-formatted certificate chain to use for the SSL connection"),
    )
    ssl_keyfile = EncryptedTextField(
        verbose_name=_("SSL key file"),
        blank=True,
        null=True,
        help_text=_("PEM-formatted private key to use for the SSL connection"),
    )

    shop = models.ForeignKey("Shop", on_delete=models.SET_NULL, related_name="smtp_accounts", null=True, blank=True)
    default_account = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shop"],
                name="unique_default_accounts",
                condition=Q(default_account=True, shop__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["default_account"],
                name="unique_global_default_account",
                condition=Q(shop=None, default_account=True),
            ),
        ]

    @classmethod
    def get_default(cls, shop=None) -> "SMTPAccount":
        try:
            return SMTPAccount.objects.get(shop=shop, default_account=True)
        except SMTPAccount.DoesNotExist:
            try:
                return SMTPAccount.objects.get(shop=None, default_account=True)
            except SMTPAccount.DoesNotExist:
                return

    def get_connection(self):
        return GetSMTPConnection(self)


class GetSMTPConnection:
    def __init__(self, smtp_account: SMTPAccount):
        self.smtp_account = smtp_account
        self._key_file = None
        self._cert_file = None

    def __enter__(self):
        connection_kwargs = dict(
            backend=settings.EMAIL_BACKEND,
            username=self.smtp_account.username,
            password=self.smtp_account.password,
            host=self.smtp_account.host,
            port=self.smtp_account.port,
            timeout=self.smtp_account.timeout,
            fail_silently=False,
            ssl_certfile=None,
            ssl_keyfile=None,
        )
        if self.smtp_account.protocol == SMTPProtocol.SSL:
            connection_kwargs["use_ssl"] = True
        else:
            connection_kwargs["use_ssl"] = False

        if self.smtp_account.protocol == SMTPProtocol.TLS:
            connection_kwargs["use_tls"] = True
        else:
            connection_kwargs["use_tls"] = False

        if self.smtp_account.ssl_certfile:
            file_descriptor, temp_certfile = tempfile.mkstemp(suffix=f"certfile_{self.smtp_account.pk}", text=True)
            self._cert_file = temp_certfile
            with fdopen(file_descriptor, "w") as certfile_file:
                certfile_file.write(self.smtp_account.ssl_certfile)
                connection_kwargs["ssl_certfile"] = self._cert_file

        if self.smtp_account.ssl_keyfile:
            file_descriptor, temp_keyfile = tempfile.mkstemp(suffix=f"keyfile_{self.smtp_account.pk}", text=True)
            self._key_file = temp_keyfile
            with fdopen(file_descriptor, "w") as keyfile_file:
                keyfile_file.write(self.smtp_account.ssl_keyfile)
                connection_kwargs["ssl_keyfile"] = self._key_file

        return mail.get_connection(**connection_kwargs)

    def __exit__(self, exc_type, exc_value, traceback):
        if self._key_file:
            os.remove(self._key_file)

        if self._cert_file:
            os.remove(self._cert_file)

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db.models import Q
from django.db.transaction import atomic

from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.shop_provider import get_shop
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.core.models import SMTPAccount
from shuup.utils.django_compat import reverse_lazy


class SMTPAccountEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = SMTPAccount
    template_name = "shuup/admin/smtp_accounts/edit.jinja"
    context_object_name = "smtp_account"
    base_form_part_classes = []
    form_part_class_provide_key = "admin_smtp_account_form_part"
    add_form_errors_as_messages = True

    def get_queryset(self):
        return SMTPAccount.objects.filter(Q(shop__isnull=True) | Q(shop=get_shop(self.request)))

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        object = self.get_object()
        delete_url = reverse_lazy("shuup_admin:smtp_account.delete", kwargs={"pk": object.pk}) if object.pk else None
        return get_default_edit_toolbar(self, save_form_id, delete_url=delete_url)

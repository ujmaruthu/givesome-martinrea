# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.urls import reverse
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.views import CreateOrUpdateView

from givesome.admin_module.forms.receipting_messages import ReceiptingMessagesForm
from givesome.models import ReceiptingMessages


class ReceiptingMessagesEditView(CreateOrUpdateView):
    model = ReceiptingMessages
    form_class = ReceiptingMessagesForm
    template_name = "givesome/admin/receipting_messages/receipting_messages.jinja"

    def get_object(self, queryset=None):
        # There will be one and only one record that contains all messages.
        return self.model.objects.first()

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.bump_cache()
        return response

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        return get_default_edit_toolbar(self, save_form_id, delete_url=None, with_split_save=False)

    def get_context_data(self, **kwargs):
        # We don't need a pk, so tell the form action to just come back here.
        kwargs["form_action"] = reverse("shuup_admin:receipting_messages.edit")
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse("shuup_admin:receipting_messages.edit")

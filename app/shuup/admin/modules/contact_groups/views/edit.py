# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from __future__ import unicode_literals

from django.db.transaction import atomic

from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.core.models import ContactGroup
from shuup.utils.django_compat import reverse_lazy

from .forms import ContactGroupBaseFormPart, ContactGroupMembersFormPart


class ContactGroupEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = ContactGroup
    template_name = "shuup/admin/contact_groups/edit.jinja"
    context_object_name = "contact_group"
    base_form_part_classes = [ContactGroupBaseFormPart, ContactGroupMembersFormPart]
    form_part_class_provide_key = "admin_contact_group_form_part"

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        object = self.get_object()
        delete_url = reverse_lazy("shuup_admin:contact_group.delete", kwargs={"pk": object.pk})
        return get_default_edit_toolbar(self, save_form_id, delete_url=delete_url if object.can_delete() else None)

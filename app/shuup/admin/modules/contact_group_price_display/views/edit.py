# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from shuup.admin.modules.contact_group_price_display.views.forms import ContactGroupPriceDisplayForm
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.core.models import ContactGroupPriceDisplay
from shuup.utils.django_compat import reverse_lazy


class ContactGroupPriceDisplayEditView(CreateOrUpdateView):
    model = ContactGroupPriceDisplay
    form_class = ContactGroupPriceDisplayForm
    template_name = "shuup/admin/contact_group_price_display/edit.jinja"
    context_object_name = "price_display"
    add_form_errors_as_messages = True

    def get_form_kwargs(self):
        kwargs = super(ContactGroupPriceDisplayEditView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy("shuup_admin:contact_group_price_display.list")

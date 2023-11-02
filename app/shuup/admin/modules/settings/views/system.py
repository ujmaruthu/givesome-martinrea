# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib import messages
from django.db.transaction import atomic
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from shuup.admin.form_part import FormPartsViewMixin
from shuup.admin.shop_provider import get_shop
from shuup.admin.toolbar import PostActionButton, Toolbar
from shuup.core.signals import settings_updated
from shuup.utils.form_group import FormGroup


class SystemSettingsView(FormPartsViewMixin, FormView):
    form_class = None
    template_name = "shuup/admin/settings/edit.jinja"
    base_form_part_classes = []
    form_part_class_provide_key = "system_settings_form_part"

    @atomic
    def form_valid(self, form):
        response = self.save_form_parts(form)
        settings_updated.send(sender=type(self), shop=get_shop(self.request))
        return response

    def get_form_parts(self, object):
        form_part_classes = self.get_form_part_classes()
        form_parts = []
        for form_part_class in form_part_classes:
            form_part = form_part_class(request=self.request, object=object)
            if form_part.has_permission():
                form_parts.append(form_part)

        form_parts.sort(key=lambda form_part: getattr(form_part, "priority", 0))
        return form_parts

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        kwargs["initial"] = dict(self.request.GET.items())
        fg = FormGroup(**kwargs)
        form_parts = self.get_form_parts(None)
        for form_part in form_parts:
            for form_def in form_part.get_form_defs():
                fg.form_defs[form_def.name] = form_def
        fg.instantiate_forms()
        return fg

    def save_form_parts(self, form):
        has_changed = False
        form_parts = self.get_form_parts(None)

        for form_part in form_parts:
            saved_form = form[form_part.name]

            if saved_form.has_changed():
                has_changed = True
                form_part.save(saved_form)

        if has_changed:
            messages.success(self.request, _("Changes saved."))
        else:
            messages.info(self.request, _("No changes detected."))

        return redirect("shuup_admin:settings.list")

    def get_context_data(self, **kwargs):
        context = super(SystemSettingsView, self).get_context_data(**kwargs)
        context["toolbar"] = Toolbar(
            [
                PostActionButton(
                    icon="fa fa-check-circle",
                    form_id="settings_form",
                    text=_("Save system settings"),
                    extra_css_class="btn-success",
                )
            ],
            view=self,
        )
        return context

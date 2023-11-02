# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.picotable import Column
from shuup.admin.utils.urls import get_model_url
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup.utils.django_compat import reverse, reverse_lazy

from givesome.models import GivesomeGif


class GivesomeGifListView(PicotableListView):
    model = GivesomeGif
    default_columns = [
        Column("gif", _("Gif"), sortable=False, linked=True, raw=True),
        Column("active", _("Active"), sortable=True),
    ]
    toolbar_buttons_provider_key = "givesome_gif_list_toolbar_provider"
    mass_actions_provider_key = "givesome_gif_list_mass_actions_provider"


class GivesomeGifEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = GivesomeGif
    template_name = "givesome/admin/checkout_gif/edit.jinja"
    context_object_name = "givesome_gif"
    base_form_part_classes = []
    form_part_class_provide_key = "admin_givesome_gif_form_part"

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        object = self.get_object()
        delete_url = reverse_lazy("shuup_admin:givesome_gif.delete", kwargs={"pk": object.pk}) if object.pk else None
        return get_default_edit_toolbar(self, save_form_id, delete_url=delete_url)

    def get_context_data(self, **kwargs):
        context = super(GivesomeGifEditView, self).get_context_data(**kwargs)
        if self.object and self.object.id:
            context["title"] = _("Givesome checkout gif")
        return context

    def form_valid(self, form):
        return self.save_form_parts(form)


class GivesomeGifDeleteView(DetailView):
    model = GivesomeGif
    context_object_name = "givesome_gif"

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(get_model_url(self.get_object()))

    def post(self, request, *args, **kwargs):
        givesome_gif = self.get_object()
        givesome_gif.delete()
        messages.success(request, _("Checkout gif has been deleted."))
        return HttpResponseRedirect(reverse("shuup_admin:givesome_gif.list"))

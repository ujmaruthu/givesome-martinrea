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
from shuup.admin.modules.services.base_form_part import PaymentMethodBaseFormPart, ShippingMethodBaseFormPart
from shuup.admin.modules.services.behavior_form_part import BehaviorComponentFormPart
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.urls import get_model_url
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.apps.provides import get_provide_objects
from shuup.core.models import PaymentMethod, ShippingMethod


class ServiceEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = None  # Override in subclass
    template_name = "shuup/admin/services/edit.jinja"
    context_object_name = "service"
    base_form_part_classes = []  # Override in subclass
    form_provide_key = "service_behavior_component_form"
    form_part_provide_key = "service_behavior_component_form_part"
    form_part_service_provider_key = None
    behavior_form_part_classes = []

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_form_parts(self, object):
        form_parts = super(ServiceEditView, self).get_form_parts(object)
        if not object.pk:
            return form_parts
        behavior_form_part_classes = []
        for form in get_provide_objects(self.form_provide_key):
            form_parts.append(self._get_behavior_form_part(form, object))
            behavior_form_part_classes.append(self._get_behavior_form_part(form, object))
        for form_class in get_provide_objects(self.form_part_provide_key):
            behavior_form_part_classes.append(form_class(self.request, object))
            form_parts.append(form_class(self.request, object))
        self.behavior_form_part_classes = behavior_form_part_classes
        if self.form_part_service_provider_key:
            for form_class in get_provide_objects(self.form_part_service_provider_key):
                form_parts.append(form_class(self.request, object))
        return form_parts

    def _get_behavior_form_part(self, form, object):
        return BehaviorComponentFormPart(self.request, form, form._meta.model.__name__.lower(), object)

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        object = self.get_object()
        delete_url = get_model_url(object, "delete") if object.pk else None
        return get_default_edit_toolbar(self, save_form_id, delete_url=(delete_url if object.can_delete() else None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["behavior_form_part"] = [form_part.name for form_part in self.behavior_form_part_classes]
        return context


class ShippingMethodEditView(ServiceEditView):
    model = ShippingMethod
    base_form_part_classes = [ShippingMethodBaseFormPart]
    form_part_service_provider_key = "service_shipping_form_part"


class PaymentMethodEditView(ServiceEditView):
    model = PaymentMethod
    base_form_part_classes = [PaymentMethodBaseFormPart]
    form_part_service_provider_key = "service_payment_form_part"

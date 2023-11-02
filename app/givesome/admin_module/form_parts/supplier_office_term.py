# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.forms import BaseModelFormSet
from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.forms import ShuupAdminFormNoTranslation

from givesome.models import SupplierOfficeTerm


class SupplierOfficeTermForm(ShuupAdminFormNoTranslation):
    class Meta:
        model = SupplierOfficeTerm
        fields = ["level", "name"]

    def __init__(self, **kwargs):
        self.supplier = kwargs.pop("supplier", None)
        super().__init__(**kwargs)


class SupplierOfficeTermFormSet(BaseModelFormSet):
    model = SupplierOfficeTerm
    form_class = SupplierOfficeTermForm
    can_delete = True
    validate_min = False
    min_num = 0
    validate_max = False
    max_num = 10
    absolute_max = 10
    can_order = False
    extra = 0

    def __init__(self, **kwargs):
        self.supplier = kwargs.pop("supplier", None)
        super().__init__(**kwargs)

    def form(self, **kwargs):
        kwargs.setdefault("supplier", self.supplier)
        return self.form_class(**kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(supplier=self.supplier)


class SupplierOfficeTermFormPart(FormPart):
    name = "office_term"
    priority = 200

    def get_initial(self):
        initial = []
        for term in SupplierOfficeTerm.objects.filter(supplier=self.object):
            initial.append({"pk": term.pk, "level": term.level, "name": term.name})
        return initial

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            SupplierOfficeTermFormSet,
            template_name="givesome/admin/vendor/supplier_office_term.jinja",
            required=False,
            kwargs={
                "initial": self.get_initial(),
                "supplier": self.object,
            },
        )

    def save(self, data):
        for term_data in data:
            # Ignore terms where level or name is empty
            if "level" not in term_data or "name" not in term_data or not term_data["name"]:
                continue

            # Delete removed videos
            if term_data["DELETE"]:
                SupplierOfficeTerm.objects.filter(supplier=self.object, level=term_data["level"]).delete()
                continue

            SupplierOfficeTerm.objects.update_or_create(
                supplier=self.object,
                level=term_data["level"],
                defaults=dict(
                    name=term_data["name"],
                ),
            )

    def form_valid(self, form_group):
        # Check that there is data to save.
        if self.name in form_group.cleaned_data:
            data = form_group.cleaned_data[self.name]
            if len(data) > 0 and data[0]:
                self.save(form_group.cleaned_data[self.name])
        return super().form_valid(form_group)

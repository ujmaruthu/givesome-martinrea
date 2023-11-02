# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from shuup.admin.form_part import TemplatedFormDef
from shuup.admin.utils.picotable import Column, TextFilter, true_or_false_filter
from shuup.core.models import Supplier
from shuup_multivendor.admin_module.form_parts.vendor import (
    VendorAddressFormPart,
    VendorBaseFormPart,
    VendorSettingsBaseFormPart,
)
from shuup_multivendor.admin_module.forms.vendor import VendorForm, VendorSettingsBaseForm
from shuup_multivendor.admin_module.views import VendorEditView, VendorListView, VendorSettingsView


class GivesomeVendorForm(VendorForm):
    """Used by admin and staff users for vendors management"""

    def __init__(self, *args, **kwargs):
        self.Meta.fields += ["content_header", "video_header", "desc"]
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = True
        self.fields.pop("revenue_percentage", None)

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if slug is None or slug == "":
            self.add_error("slug", _("Slug must be provided for vendors."))
        if slug is not None:
            # TODO? - Validate slug against existing URLs (eg. /admin, /p)
            if len(slug) < 3:
                self.add_error("slug", _("Slug is too short."))
            if self.instance.pk:
                existing_slugs = Supplier.objects.exclude(pk=self.instance.pk).values_list("slug", flat=True)
            else:
                existing_slugs = Supplier.objects.values_list("slug", flat=True)
            if slug in existing_slugs:
                self.add_error("slug", _("Slug is already in use by another vendor."))
        return slug


class GivesomeVendorSettingsBaseForm(VendorSettingsBaseForm):
    """Used by vendors to change current vendor settings"""

    class Meta(VendorSettingsBaseForm.Meta):
        exclude = ["slug"]


class GivesomeVendorBaseFormPart(VendorBaseFormPart):
    """Used by admin and staff users for vendors management"""

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            GivesomeVendorForm,
            template_name="shuup_multivendor/admin/vendor/_edit_base_form.jinja",
            required=True,
            kwargs={
                "instance": self.object,
                "request": self.request,
                "languages": settings.LANGUAGES,
            },
        )

    def form_valid(self, form):
        self.object = form["base"].save()


class GivesomeVendorSettingsBaseFormPart(VendorSettingsBaseFormPart):
    """Used by vendors to change current vendor settings"""

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            GivesomeVendorSettingsBaseForm,
            template_name="shuup_multivendor/admin/vendor/_edit_base_form.jinja",
            required=True,
            kwargs={
                "instance": self.object,
                "request": self.request,
                "languages": settings.LANGUAGES,
            },
        )


class GivesomeVendorEditView(VendorEditView):
    """View used by admin and staff users for vendors management"""

    base_form_part_classes = [GivesomeVendorBaseFormPart, VendorAddressFormPart]


class GivesomeVendorSettingsView(VendorSettingsView):
    """View used by vendors to change current vendor settings"""

    base_form_part_classes = [GivesomeVendorSettingsBaseFormPart, VendorAddressFormPart]


class GivesomeVendorListView(VendorListView):
    """View used by admin and staff users for vendors management"""

    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="name",
            display="name",
            filter_config=TextFilter(filter_field="name", placeholder=_("Filter by name...")),
        ),
        Column("users", _("Management Users"), display="get_vendor_users", sortable=False),
        Column("vendor_type", _("Vendor Type"), display="get_vendor_type", sort_field="givesome_extra__vendor_type"),
        Column(
            "is_approved", _("Is approved"), display="get_approved", sortable=True, filter_config=true_or_false_filter
        ),
    ]

    def get_vendor_type(self, instance):
        if hasattr(instance, "givesome_extra"):
            return instance.givesome_extra.vendor_type.label
        return _("UNKNOWN")

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.exceptions import ValidationError
from django.forms import HiddenInput, forms
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from shuup.admin.forms import ShuupAdminFormNoTranslation
from shuup.admin.forms.fields import Select2ModelMultipleField
from shuup.admin.supplier_provider import get_supplier
from shuup.core.models import Supplier

from givesome.enums import VendorExtraType
from givesome.models import GivesomeOffice, SustainabilityGoal


class OfficeForm(ShuupAdminFormNoTranslation):
    class Meta:
        model = GivesomeOffice
        fields = ("supplier", "name", "ordering", "disabled", "parent")
        labels = {"supplier": "Branded Vendor"}

    def __init__(self, **kwargs):
        """Restrict supplier choices to brand vendors, or authenticated vendor"""
        self.request = kwargs.pop("request", None)
        super().__init__(**kwargs)
        supplier = get_supplier(self.request)

        supplier_qs = Supplier.objects.filter(
            enabled=True,
            givesome_extra__isnull=False,
            givesome_extra__vendor_type=VendorExtraType.BRANDED_VENDOR,
        )
        if supplier:
            supplier_qs = supplier_qs.filter(id=supplier.id)
            self.initial["supplier"] = supplier.id
            self.fields["supplier"].widget = HiddenInput()
        self.fields["supplier"].queryset = supplier_qs

        # Available offices are further filtered with js on the form
        office_queryset = GivesomeOffice.objects.filter(disabled=False).exclude(id=kwargs["instance"].pk)
        self.fields["parent"].queryset = office_queryset
        self.fields["parent"].choices = [(None, "----")] + [(o.pk, force_text(o)) for o in office_queryset]
        if self.instance.parent is not None:
            # Can't disable being disabled if any parent is disabled
            if self.instance.get_ancestors().filter(disabled=True).exists():
                self.fields["disabled"].disabled = True

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        supplier = self.cleaned_data.get("supplier")
        if parent:
            if supplier != parent.supplier:
                raise ValidationError(_("Can't set parent office, as it's belongs to a different supplier."))
            if self.instance in parent.get_ancestors():
                raise ValidationError(
                    _(
                        "Can't create a circular reference to an office. "
                        "This office is already an ancestor of the selected office."
                    )
                )
        return parent

    def save(self, commit=True):
        super().save(commit=commit)
        # Set all children's disabled state to match parent's state
        if "disabled" in self.changed_data:
            self.instance.get_descendants().update(disabled=self.cleaned_data["disabled"])
        return self.instance


class SustainabilityGoalSelectionForm(forms.Form):
    sustainability_goals = Select2ModelMultipleField(
        SustainabilityGoal,
        required=False,
        help_text="Begin typing key words relating to the Sustainable Development Goals you wish to feature.",
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        existing_goals = []
        if kwargs.get("initial"):
            existing_goals = [(goal.id, goal) for goal in kwargs.pop("initial").first().goals.all()]
        super().__init__(*args, **kwargs)
        # Note: odd as it looks, the following combination of initial/choices is necessary for the initial
        # value to render properly.
        self.fields["sustainability_goals"].initial = [goal[0] for goal in existing_goals]
        self.fields["sustainability_goals"].widget.choices = existing_goals

    def clean_sustainability_goals(self):
        goals = self.cleaned_data["sustainability_goals"]
        if len(goals) > 3:
            raise ValidationError("Please choose only three Sustainable Development Goals")
        return goals

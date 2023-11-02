# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shuup.admin.forms import ShuupAdminFormNoTranslation
from shuup.core.models import Supplier

from givesome.models import Givecard, GivecardBatch, GivecardCampaign


class CampaignModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        """Use custom label for campaign selection dropdown"""

        supplier = ""
        if obj.supplier is not None:
            supplier = f" - {obj.supplier.name}"

        return f"{obj.identifier} ({str(obj)}){supplier}"


class GivecardBatchForm(ShuupAdminFormNoTranslation):
    """Used for creating Unique Givecard Batches and editing both Unique and Multicard Batches"""

    class Meta:
        model = GivecardBatch
        fields = [
            "campaign",
            "supplier",
            "office",
            "redirect_office",
            "restriction_type",
            "value",
            "amount",
            "code",
            "redemption_start_date",
            "redemption_end_date",
            "expiration_date",
            "expiry_type",
            "archived",
        ]
        labels = {
            "supplier": _("Branded Vendor Restriction"),
            "office": _("Office Restriction"),
            "amount": _("Quantity"),
            "value": _("Value ($)"),
        }

    campaign = CampaignModelChoiceField(queryset=GivecardCampaign.objects.all(), required=False)
    is_multicard = False

    def _is_multicard(self):
        if self.instance and self.instance.code is not None:
            return True
        return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["redemption_end_date"].required = True

        # Restrictions can apply to either branded vendors or charities.
        qs = Supplier.objects.filter(enabled=True, givesome_extra__isnull=False)
        self.fields["supplier"].queryset = qs

        # Order offices based on level
        self.fields["office"].queryset = self.fields["office"].queryset.order_by("level")

        if not self._is_multicard():
            self.fields.pop("code", None)
        else:
            # Code is required for Multicards
            self.fields["code"].required = True
            # Restrict changing code if any redeemed givecards exist
            if self.instance and self.instance.pk and self.instance.givecards_redeemed > 0:
                self.fields["code"].disabled = False

        # Batch exists and Givecards are generated
        if self.instance and self.instance.pk:
            if (
                self.instance.redemption_end_date is not None
                and self.instance.redemption_end_date < timezone.now().date()
            ) or (self.instance.expiration_date is not None and self.instance.expiration_date < timezone.now().date()):
                # Amount or Value can't be changed if batch is expired
                self.fields["amount"].disabled = False
                self.fields["value"].disabled = False

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if self.instance and self.instance.pk and "amount" in self.changed_data:
            givecards_count = self.instance.givecards.count()
            # Amount is being reduced
            if givecards_count > 0 and givecards_count > amount:
                # Validate that requested amount of Givecards can be safely deleted.
                deletable_givecards_count = self.instance.givecards.filter(redeemed_on__isnull=True).count()
                if deletable_givecards_count < givecards_count - amount:
                    raise ValidationError(
                        _(
                            "Not enough unredeemed Givecards to reduce quantity to {}. "
                            "Minimum allowed quantity is {}"
                        ).format(amount, (givecards_count - deletable_givecards_count))
                    )
        return amount

    def clean_value(self):
        value = self.cleaned_data["value"]
        if self.instance and self.instance.pk and "value" in self.changed_data:
            if not self.instance.givecards.filter(redeemed_on__isnull=True).exists():
                raise ValidationError(_("Batch doesn't have any unredeemed Givecards. Unable to modify value."))
        return value

    def save(self, commit=True):
        """Generate givecards on successful batch creation"""
        instance = super().save()
        if instance.pk:
            givecards_count = instance.givecards.count()
            if "amount" in self.changed_data:
                # Generate missing givecards
                if givecards_count < instance.amount:
                    instance.generate_givecards()
                # Delete extra Givecards that exceed the set quantity
                else:
                    deleted_count = givecards_count - instance.amount
                    deleted_givecards = instance.givecards.filter(redeemed_on__isnull=True)[:deleted_count].values("id")
                    Givecard.objects.filter(pk__in=deleted_givecards).delete()
            if "value" in self.changed_data:
                # Changing value is validated in clean_value()
                # Update the balance of only unredeemed Givecards.
                # This may lead to incorrect reporting values, but the customer is aware of the fact.
                instance.givecards.filter(redeemed_on__isnull=True).update(balance=instance.value)
        return instance


class MulticardBatchForm(GivecardBatchForm):
    """Used only when creating Multicard Batches"""

    def _is_multicard(self):
        return True

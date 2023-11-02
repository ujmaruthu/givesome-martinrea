# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import re
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import ExpressionWrapper, F, IntegerField, Q
from django.db.models.aggregates import Sum
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumIntegerField
from shuup.core.models import Product, ShuupModel

from givesome.enums import GivecardBatchExpiryType, GivecardDonateRestrictionType
from givesome.givecard_utils import generate_new_codes
from givesome.models import Givecard


class GivecardBatchQuerySet(models.QuerySet):
    def expired(self):
        """Returns batches that have already expired"""
        return self.filter(expiration_date__lt=timezone.localdate())

    def redeemable(self):
        """Filters qs to Batches that contain at least one redeemable givecard"""
        grace_period = timezone.localtime() - timedelta(days=settings.GIVESOME_MULTICARD_REDEEM_GRACE_PERIOD_DAYS)
        today = timezone.localdate()

        return (
            self.exclude(
                expiration_date__lt=today,
            )
            .exclude(redemption_start_date__gt=today)
            .exclude(redemption_end_date__lt=today)
            .filter(
                campaign__isnull=False,
                givecards__balance__gt=0,
                givecards__user=None,
            )
            .filter(Q(givecards__redeemed_on__lt=grace_period) | Q(givecards__redeemed_on__isnull=True))
            .distinct()
        )

    def has_balance(self):
        """Returns batches that's Givecards have any balance left"""
        return self.filter(givecards__balance__gt=0).distinct()

    def annotate_current_balance(self):
        return self.annotate(current_balance=Sum("givecards__balance"))

    def annotate_original_balance(self):
        return self.annotate(
            original_balance=Coalesce(ExpressionWrapper(F("amount") * F("value"), output_field=IntegerField()), 0)
        )


class GivecardBatch(ShuupModel):
    created_on = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_("created on"))
    generated_on = models.DateTimeField(blank=True, null=True, verbose_name=_("generated on"))
    campaign = models.ForeignKey(
        "givesome.GivecardCampaign",
        related_name="batches",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("givecard campaign"),
        help_text=_("Related Givecard Campaign. This is required to enable Givecard redemption."),
    )
    restriction_type = EnumIntegerField(
        GivecardDonateRestrictionType,
        default=GivecardDonateRestrictionType.DISABLED,
        verbose_name=_("Donation restriction type"),
        help_text=_(
            "Defines how Givecards are allowed to be donated. "
            "Office - Givecards can only be used on this Office's branded page. "
            "Supplier - Givecards can only be used on vendor's and it's office's branded pages. "
            "Disabled - No donation restrictions."
        ),
    )
    supplier = models.ForeignKey(
        "shuup.Supplier",
        related_name="batches",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("branded vendor"),
        help_text=_(
            "When user redeems a Givecard they will be redirected to this vendor's branded page. "
            "Givecards may also be restricted to this vendor depending on set 'Donation restriction type'"
        ),
    )
    office = models.ForeignKey(
        "givesome.GivesomeOffice",
        related_name="batches",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("office"),
        help_text=_(
            "When user redeems a Givecard they will be redirected to this office's branded page. "
            "Givecards may also be restricted to this office depending on set 'Donation restriction type'"
        ),
    )
    redirect_office = models.ForeignKey(
        "givesome.GivesomeOffice",
        related_name="redirect_batches",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("redirect office"),
        help_text=_(
            "When user redeems a Givecard they will be redirected to this office's branded page. "
            "This field overrides `Restricted Supplier` and `Restricted Office`, and affects only redirecting. "
            "Requires selecting a `Restricted Supplier` and `Restricted Office` first, as this field contains only"
            "sub-offices. Requires this office to be hierarchically underneath selected office on above field"
        ),
    )
    redemption_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Redemption start date"),
        help_text=_("The date and time the Givecard redemption starts. Givecards are not redeemable before this time."),
    )
    redemption_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Redemption end date"),
        help_text=_("The date and time the Givecard redemption ends. Givecards are not redeemable after this time."),
    )
    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Expiration date"),
        help_text=_(
            "The date and time on which the Givecard expires. "
            "After this it is no longer able to be used, and it will be hidden in donor wallets."
        ),
    )
    expiry_type = EnumIntegerField(
        GivecardBatchExpiryType,
        default=GivecardBatchExpiryType.AUTOMATIC,
        verbose_name=_("Expiration type"),
        help_text=_(
            "Action taken when Givecard Batch expires. "
            "Automatic - Funds are automatically reallocated to active projects through a preset process. "
            "Manual - Funds are redirected to Givesome Purse to be manually reallocated to projects. "
            "Disabled - Funds are not reallocated to projects, but managed outside Shuup. "
        ),
    )
    amount = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100000)],  # some sane values
        verbose_name=_("quantity"),
        help_text=_("Quantity of Givecards to generate in this batch."),
    )
    value = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(2), MaxValueValidator(100000)],
        verbose_name=_("value"),
        help_text=_("Value ($) on all the Givecards generated in this batch."),
    )
    code = models.CharField(
        max_length=6,
        blank=True,
        null=True,  # Blank for Unique Givecards
        verbose_name=_("PIN"),
        help_text=_(
            "Used for givecard redemption. Required for Multicards. "
            "This code will be the same for all Multicards in this batch."
        ),
    )
    archived = models.BooleanField(
        default=False,
        verbose_name=_("Archived"),
        help_text=_("Archived Givecard Batches are excluded on Vendor dashboards."),
    )

    objects = GivecardBatchQuerySet.as_manager()

    class Meta:
        verbose_name_plural = _("givecard batches")
        ordering = ("-created_on",)

    def __str__(self):
        batch_type = self.code and "Multicard" or "Givecard"
        pk = self.code and self.code or self.pk
        suffix = self.givecards.all().exists() and f" [{self.amount} x ${self.value}]" or ""
        return f"{batch_type} Batch ({pk}){suffix}"

    def clean(self):
        if self.code is not None:
            self.clean_code()

        if self.redemption_start_date is not None:
            if self.redemption_end_date is not None:
                if self.redemption_start_date > self.redemption_end_date:
                    raise ValidationError(_("Redemption start date can not be after end date."))
            if self.expiration_date is not None:
                if self.redemption_start_date > self.expiration_date:
                    raise ValidationError(_("Redemption start date can not be after expiration date."))

        if self.redemption_end_date is not None and self.expiration_date is not None:
            if self.redemption_end_date > self.expiration_date:
                raise ValidationError(_("Redemption end date can not be after expiration date."))

        if self.office:
            if not self.supplier:
                raise ValidationError(_("Supplier is required if office is set."))
            if self.office.supplier != self.supplier:
                raise ValidationError(_("Office needs to belong selected supplier."))

    def clean_code(self):
        self.code = self.code.upper()

        # Validate code uniqueness
        if GivecardBatch.objects.filter(code=self.code).exclude(pk=self.pk).exists():
            raise ValidationError(_("A Multicard with given code already exists."))
        elif Givecard.objects.filter(code=self.code).exists():
            raise ValidationError(_("A Givecard with given code already exists."))

        if not re.search(r"^[A-Z0-9]{6}$", self.code):  # 6 capital letters
            raise ValidationError(_("PIN format is invalid."))

    def generate_givecards(self):
        missing_givecards_quantity = self.amount - self.givecards.count()
        if missing_givecards_quantity <= 0:
            raise ValidationError(_("Enough Givecards have already been generated."))

        if self.code:
            # Multicards
            self.clean_code()  # Validate code is unique before generating
            Givecard.objects.bulk_create(
                [Givecard(batch=self, balance=self.value, code=None) for __ in range(0, missing_givecards_quantity)]
            )
        else:
            # Unique Givecards
            codes = generate_new_codes(missing_givecards_quantity)
            Givecard.objects.bulk_create([Givecard(batch=self, balance=self.value, code=code) for code in codes])
        self.generated_on = timezone.localtime()
        self.save()
        return self

    def get_redemption_errors(self):
        """Yields an error for every reason batch is unable to be redeemed"""
        today = timezone.localdate()
        if self.campaign is None:
            yield ValidationError(_("Givecard Batch does not have a campaign set."))
        if self.redemption_start_date is not None and self.redemption_start_date > today:
            yield ValidationError(_("Givecard Batch redemption has not started yet."))
        if self.redemption_end_date is not None and self.redemption_end_date < today:
            yield ValidationError(_("Givecard Batch redemption has already ended."))
        if self.expiration_date is not None and self.expiration_date < today:
            yield ValidationError(_("Givecard Batch has expired."))
        if not self.givecards.redeemable().exists():
            yield ValidationError(_("Multicard does not have any valid Givecards"))

    def is_redeemable(self):
        """
        Returns true if batch has any redeemable children
        Works for both Unique Givecards and Multicards
        """
        return not any(self.get_redemption_errors())

    def get_best_multicard(self):
        """
        Select the best Multicard to give to a user.
        Multicard is selected based on:
        1. Not redeemed before
        2. Highest balance left on card
        3. Oldest previously redeemed card

        Non-claimed Multicards redeemed in the last 1 day are locked
        to prevent another user from claiming the same card.
        """
        givecards = (
            self.givecards.redeemable()
            .extra(
                select={
                    "redeemed_on_isnull": "redeemed_on IS NULL",
                }
            )
            .order_by("-redeemed_on_isnull", "-balance", "redeemed_on")
        )
        return givecards.first()

    def redeem(self, user=None):
        """
        If user is given, claim Multicard for user
        User is optional to allow Anonymous users to redeem Multicards
        """
        if self.code is None:
            raise ValidationError(_("Unable to redeem non-Multicard batches."))
        if self.is_redeemable():
            givecard = self.get_best_multicard()
            if givecard:
                givecard.redeem(user)
                return givecard
        raise ValidationError(_("Multicard is not redeemable."))

    def get_projects_donated_to(self):
        return Product.objects.filter(
            order_lines__order__payments__purchase_report_data__givecard__in=self.givecards.filter(
                redeemed_on__isnull=False
            )
        ).distinct()

    def is_nullifiable(self):
        return (
            (
                self.expiration_date is None
                or (self.expiration_date is not None and timezone.localdate() >= self.expiration_date)
            )
            and self.expiry_type == GivecardBatchExpiryType.MANUAL
            and self.total_balance > 0
        )

    def nullify(self, nullifier):
        """Empty all givecards of remaining funds, and create a record of it."""
        if not self.is_nullifiable():
            raise ValidationError("Unable to nullify Givecard Batch")

        nullified_batch = NullifiedGivecardBatch.objects.create(
            batch=self, amount=self.total_balance, nullified_by=nullifier
        )
        self.givecards.all().update(balance=0)
        return nullified_batch

    @property
    def total_balance(self):
        """Return the total amount of balance left in this batch's Givecards"""
        if not self.givecards.exists():
            return 0
        return self.givecards.all().aggregate(sum_balance=Sum("balance"))["sum_balance"] or 0

    @property
    def original_balance(self):
        if not self.givecards.exists():
            return 0
        return self.amount * self.value

    @property
    def givecards_redeemed(self):
        return self.givecards.filter(redeemed_on__isnull=False).count()

    @property
    def projects_donated_count(self):
        return self.get_projects_donated_to().count()

    @property
    def total_lives_impacted(self):
        return (
            self.get_projects_donated_to().aggregate(sum_lives_impacted=Sum("project_extra__lives_impacted"))[
                "sum_lives_impacted"
            ]
            or 0
        )

    @property
    def total_amount_donated(self):
        """Returns amount of $ donated by users in the frontend through checkout"""
        from givesome.models import PurchaseReportData

        return (
            PurchaseReportData.objects.filter(givecard__in=self.givecards.all()).aggregate(
                sum_donated=Cast(Sum("payment__amount_value"), IntegerField())
            )["sum_donated"]
            or 0
        )


class NullifiedGivecardBatch(ShuupModel):
    batch = models.ForeignKey(GivecardBatch, on_delete=models.PROTECT)
    amount = models.IntegerField()
    nullified_on = models.DateField(auto_now=True)
    nullified_by = models.ForeignKey("shuup.PersonContact", on_delete=models.PROTECT)

    def __str__(self):
        return f"Nullified {self.batch}"

    def clean(self):
        if self.batch.expiration_date > timezone.localdate():
            raise ValidationError(_("Batch is not expired yet."))
        if self.batch.expiry_type != GivecardBatchExpiryType.MANUAL:
            raise ValidationError(_("Batch does not have expiry type of Manual."))
        if self.amount <= 0:
            raise ValidationError(_("Batch has no balance left to nullify."))

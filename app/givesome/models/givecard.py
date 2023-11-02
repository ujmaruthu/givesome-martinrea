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
from typing import TYPE_CHECKING, Optional, Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, F, IntegerField, Q, Value, When
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import ShuupModel, Supplier

from givesome.currency_conversion import givesome_exchange_currency
from givesome.enums import GivecardDonateRestrictionType

if TYPE_CHECKING:
    from givesome.models import GivesomeOffice


class GivecardQuerySet(models.QuerySet):
    def usable(self):
        """Filters qs to Givecards that can be used on a project"""
        return (
            self.exclude(batch__expiration_date__lt=timezone.localdate())
            .exclude(  # These vendors don't have a page so givecards aren't usable
                Q(batch__supplier__givesome_extra__allow_brand_page=False)
                & ~Q(batch__restriction_type=GivecardDonateRestrictionType.DISABLED)
            )
            .filter(batch__campaign__isnull=False, balance__gt=0)
        )

    def filter_promoter_usable_givecards(self, promoter: Optional[Union[Supplier, "GivesomeOffice"]] = None):
        """
        Filters to Givecards that are usable on projects promoted by given promoter.
        Will always include Non-restricted Givecards.
        """
        from givesome.models import GivesomeOffice

        qs = self.usable()
        # Non-restricted Givecards are always returned
        filters = Q(batch__supplier=None) | Q(batch__restriction_type=GivecardDonateRestrictionType.DISABLED)
        if promoter is None:
            return qs.filter(filters)

        promoter_class = promoter.__class__
        if issubclass(promoter_class, Supplier):
            filters |= Q(batch__supplier=promoter, batch__restriction_type=GivecardDonateRestrictionType.SUPPLIER)
            filters |= Q(
                batch__office=None,
                batch__supplier=promoter,
                batch__restriction_type=GivecardDonateRestrictionType.OFFICE,
            )

        if issubclass(promoter_class, GivesomeOffice):
            filters |= Q(
                batch__supplier=promoter.supplier, batch__restriction_type=GivecardDonateRestrictionType.SUPPLIER
            )
            filters |= Q(
                batch__supplier=promoter.supplier,
                batch__office=None,
                batch__restriction_type=GivecardDonateRestrictionType.OFFICE,
            )
            if promoter.level == 0:  # Shortcut to reduce db hits a little
                filters |= Q(batch__office=promoter, batch__restriction_type=GivecardDonateRestrictionType.OFFICE)
            else:
                # Promoter-office and all of its ancestors are valid
                ancestor_office_ids = promoter.get_ancestors(include_self=True).values_list("pk", flat=True)
                filters |= Q(
                    batch__office_id__in=ancestor_office_ids,
                    batch__restriction_type=GivecardDonateRestrictionType.OFFICE,
                )

        return qs.filter(filters)

    def is_checkout_possible(self, promoter: Optional[Union[Supplier, "GivesomeOffice"]] = None) -> bool:
        """Find out if it is possible to donate with any of the supplied givecards."""
        return self.filter_promoter_usable_givecards(promoter).exists()

    def order_for_checkout(self):
        """
        Orders Givecards for checkout.
        Givecards are returned in the order they should be used.

        First Givecards have the most strict restrictions, last do not have any.
        If there are many Givecards with similar restrictions, they are ordered by expiry date.

        Givecards can be sorted into three groups:
        1. Office Restriction
            1.1.    OFFICE is set and   SUPPLIER is set and     RESTRICTION_TYPE is OFFICE
        2. Supplier Restriction
            2.1.    -                   SUPPLIER is set and     RESTRICTION_TYPE is OFFICE
            2.2.    -                   SUPPLIER is set and     RESTRICTION_TYPE is SUPPLIER
            2.3.    OFFICE is set and   SUPPLIER is set and     RESTRICTION_TYPE is SUPPLIER
        3. No Restriction
            3.1.    -                   -                       *
            3.2.    *                   *                       RESTRICTION_TYPE is DISABLED

        Lastly:
        Givecards that have an office set are sorted based on the level of the office, deepest first
        Givecards with earlier expiry date are ordered first
        Givecards with no expiry date come after any expiry dates
        """
        office_set = Q(batch__office__isnull=False)
        office_null = Q(batch__office__isnull=True)
        supplier_set = Q(batch__supplier__isnull=False)
        restriction_office = Q(batch__restriction_type=GivecardDonateRestrictionType.OFFICE)
        restriction_supplier = Q(batch__restriction_type=GivecardDonateRestrictionType.SUPPLIER)

        return self.annotate(
            ordering=Case(
                When(office_set & supplier_set & restriction_office, then=Value(0)),
                When(
                    (office_null & supplier_set & restriction_office) | (supplier_set & restriction_supplier),
                    then=Value(1),
                ),
                default=Value(2),
                output_field=IntegerField(),
            ),
        ).order_by(
            "ordering",
            F("batch__office__level").desc(nulls_last=True),  # Use more restrictive offices first
            F("batch__expiration_date").asc(nulls_last=True),
            "batch__exp_date",
        )

    def redeemable(self):
        """
        Filters qs to Givecards that can be redeemed
        Also returns Multicard Givecards
        """

        # Period during which Multicards can't be redeemed again
        grace_period = timezone.localtime() - timedelta(days=settings.GIVESOME_MULTICARD_REDEEM_GRACE_PERIOD_DAYS)
        today = timezone.localdate()
        return (
            self.usable()
            .exclude(redeemed_on__gte=grace_period, batch__code__isnull=False)
            .exclude(batch__redemption_start_date__gt=today)
            .exclude(batch__redemption_end_date__lt=today)
            .filter(user=None)
        )


class Givecard(ShuupModel):
    batch = models.ForeignKey(
        "givesome.GivecardBatch",
        related_name="givecards",
        on_delete=models.CASCADE,
        verbose_name=_("givecard batch"),
        help_text=_("Related Givecard Campaign."),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="givecards",
        on_delete=models.SET_NULL,
        editable=False,
        blank=True,
        null=True,  # Set when redeemed
        help_text=_("User that has redeemed this givecard."),
    )
    code = models.CharField(
        max_length=6,
        blank=True,
        null=True,  # Blank for multicards
        verbose_name=_("PIN"),
        help_text=_("Used for givecard redemption."),
    )
    balance = models.PositiveIntegerField(verbose_name=_("value"), help_text=_("Balance ($) left on this givecard"))
    redeemed_on = models.DateTimeField(editable=False, blank=True, null=True, verbose_name=_("redeemed on"))
    automatically_donated = models.PositiveIntegerField(
        default=0,
        verbose_name=_("automatically donated amount"),
        help_text=_("Balance ($) from this givecard that was donated automatically"),
    )

    objects = GivecardQuerySet.as_manager()

    def clean(self):
        if self.code is not None:
            self.clean_code()

    def clean_code(self):
        from givesome.models import GivecardBatch

        self.code = self.code.upper()

        # Validate code uniqueness
        if GivecardBatch.objects.filter(code=self.code).exists():
            raise ValidationError(_("A Multicard with given code already exists."))
        elif Givecard.objects.filter(code=self.code).exclude(pk=self.pk).exists():
            raise ValidationError(_("A Givecard with given code already exists."))

        if not re.search(r"^[A-Z0-9]{6}$", self.code):  # 6 capital letters
            raise ValidationError(_("PIN format is invalid."))

    def get_redemption_errors(self, user=None):
        """Yields an error for every reason batch is unable to be redeemed"""
        today = timezone.localdate()
        if self.user is not None:
            yield ValidationError(_("This PIN has already been used."), code="visible_for_user")
        if self.balance == 0:
            yield ValidationError(_("Givecard has no balance left."))
        if self.batch.campaign is None:
            yield ValidationError(_("Givecard does not have a campaign set."))
        if self.code is None and user is not None and self.batch.givecards.filter(user=user).exists():
            yield ValidationError(_("This PIN has already been used!"), code="visible_for_user")
        if self.batch.expiration_date is not None and self.batch.expiration_date < today:
            yield ValidationError(_("Givecard has already expired."), code="visible_for_user")
        if self.batch.redemption_end_date is not None and self.batch.redemption_end_date < today:
            yield ValidationError(_("Givecard redemption has already ended."), code="visible_for_user")
        if self.batch.redemption_start_date is not None and self.batch.redemption_start_date > today:
            yield ValidationError(_("Givecard redemption has not started yet."))
        supplier = self.batch.supplier
        if (
            supplier is not None
            and supplier.givesome_extra.allow_brand_page is False
            and self.batch.restriction_type != GivecardDonateRestrictionType.DISABLED
        ):
            yield ValidationError(_("Supplier brand page is disabled."))

    def is_redeemable(self, user=None):
        return not any(self.get_redemption_errors(user))

    def redeem(self, user=None):
        """
        If user is given, claim Givecard for user
        User is optional to allow Anonymous users to redeem Givecards
        """
        if self.is_redeemable(user):
            if user is not None:
                self.user = user
            self.redeemed_on = timezone.localtime()
            self.save()
            return self
        raise ValidationError(_("Givecard is not redeemable."))

    def is_givecard_expiring_soon(self) -> bool:
        if self.batch.expiration_date is None:
            return False
        expiring_soon_cutoff = timezone.localdate() + timedelta(days=7)
        return self.batch.expiration_date < expiring_soon_cutoff

    def get_code(self) -> str:
        if self.code is not None:
            return self.code
        elif self.batch.code is not None:
            return self.batch.code
        raise ValueError("Unable to read Givecard code")

    def get_data_for_wallet(self) -> dict:
        """
        Return a dict containing data necessary to add it to a session storage wallet
        Supplier and Office will be included only if they are restrictions on the Batch
        """

        data = {
            "id": self.pk,
            "code": self.get_code(),
            "preferred_currency_balance": givesome_exchange_currency(self.user, self.balance),
            "balance": self.balance,
            "campaign": self.batch.campaign.id if self.batch.campaign is not None else 0,
            "campaign_name": self.batch.campaign.name if self.batch.campaign is not None else "",
            "is_expiring_soon": self.is_givecard_expiring_soon(),
        }

        if self.batch.expiration_date is not None:
            data["exp_date"] = self.batch.expiration_date
        if self.batch.supplier is not None and self.batch.restriction_type != GivecardDonateRestrictionType.DISABLED:
            data["supplier"] = self.batch.supplier.pk
            data["supplier_name"] = self.batch.supplier.name
            if self.batch.office is not None and self.batch.restriction_type == GivecardDonateRestrictionType.OFFICE:
                data["office"] = self.batch.office.pk
                data["office_name"] = self.batch.office.name
        return data

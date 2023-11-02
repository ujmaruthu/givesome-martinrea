# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, ExpressionWrapper, F, FloatField, IntegerField, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Cast
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from filer.fields.image import FilerImageField
from parler.models import TranslatableModel, TranslatedFields
from shuup.core.fields import InternalIdentifierField
from shuup.core.models import Order, Payment, PaymentMethod, Product, ShuupModel
from shuup_stripe_multivendor.models import StripeMultivendorPaymentProcessor

from givesome.admin_module.utils import CoalesceZero, SQCount, SQSum
from givesome.models import Givecard, GivecardBatch


class GivecardCampaignQuerySet(models.QuerySet):
    def annotate_percentage_redeemed(self, hide_archived_batches=False):
        """
        Percentage of Givecards from this Campaign that are redeemed

        Output fields:
            sum_redeemed_givecards
            sum_givecards
            percentage_redeemed
        """
        filters = Q()
        if hide_archived_batches is True:
            filters |= Q(archived=False)
        return self.annotate(
            # SubQueries are used to reduce amount of joins when annotating other values.
            # This increases performance a ton when fetching thousands of Givecards
            sum_redeemed_givecards=SQSum(
                GivecardBatch.objects.filter(filters, campaign_id=OuterRef("pk"))
                .annotate(redeemed_givecards=Count("givecards", filter=Q(givecards__redeemed_on__isnull=False)))
                .values("redeemed_givecards"),
                sum_field="redeemed_givecards",
            ),
            sum_givecards=SQSum(
                GivecardBatch.objects.filter(filters, campaign_id=OuterRef("pk"))
                .annotate(givecards_count=Count("givecards"))
                .values("givecards_count"),
                sum_field="givecards_count",
            ),
            percentage_redeemed=ExpressionWrapper(
                Cast(F("sum_redeemed_givecards"), FloatField()) / Cast(F("sum_givecards"), FloatField()) * 100,
                output_field=IntegerField(),
            ),
        )

    def aggregate_givecards_redeemed(self, hide_archived_batches=False):
        """Returns the percentage of Givecards from all QS Campaigns are redeemed"""
        return (
            self.annotate_percentage_redeemed(hide_archived_batches).aggregate(
                aggr_percentage_redeemed=ExpressionWrapper(
                    Sum("sum_redeemed_givecards") / Sum("sum_givecards") * 100, output_field=FloatField()
                )
            )["aggr_percentage_redeemed"]
            or 0
        )

    def annotate_balances(self, hide_archived_batches=False):
        """
        Amount of balances left on Givecards from this Campaign

        Output fields:
            current_balance
            original_balance
        """
        filters = Q()
        if hide_archived_batches is True:
            filters |= Q(archived=False)
        return self.annotate(
            current_balance=CoalesceZero(
                SQSum(
                    GivecardBatch.objects.filter(filters, campaign__id=OuterRef("pk"))
                    .annotate_current_balance()
                    .values("current_balance"),
                    sum_field="current_balance",
                ),
            ),
            original_balance=CoalesceZero(
                SQSum(
                    GivecardBatch.objects.filter(filters, campaign__id=OuterRef("pk"))
                    .annotate_original_balance()
                    .values("original_balance"),
                    sum_field="original_balance",
                ),
            ),
        )

    def annotate_count_projects_donated(self, hide_archived_batches=False):
        """
        Amount of unique projects donated to with Givecards from this Campaign

        Output field: count_projects_donated
        """
        filters = Q()
        if hide_archived_batches is True:
            filters |= Q(archived=False)
        return self.annotate(
            count_projects_donated=SQCount(
                GivecardBatch.objects.filter(
                    filters, campaign__id=OuterRef("pk"), givecards__purchase_report_data__project__isnull=False
                )
                .values("givecards__purchase_report_data__project")
                .order_by("givecards__purchase_report_data__project_id")  # Required for distinct to work
                .distinct(),
            ),
        )

    def aggregate_count_projects_donated(self, hide_archived_batches=False):
        """Returns the amount of unique projects donated to with Givecards from all Campaigns in this QS"""
        filters = Q()
        if hide_archived_batches is True:
            filters |= Q(archived=False)
        return (
            GivecardBatch.objects.filter(
                filters,
                campaign_id__in=self.values_list("pk", flat=True),
                givecards__purchase_report_data__project__isnull=False,
            )
            .values("givecards__purchase_report_data__project_id")
            .distinct()
            .count()
            or 0
        )

    def annotate_total_amount_donated(self, hide_archived_batches=False):
        """
        Amount of $ users have donated with Givecards from this Campaign
        This does not take into account any automatic donations

        Output field: total_amount_donated
        """
        filters = Q()
        if hide_archived_batches is True:
            filters |= Q(purchase_report_data__givecard__batch__archived=False)
        return self.annotate(
            total_amount_donated=CoalesceZero(
                SQSum(
                    Payment.objects.filter(
                        filters, purchase_report_data__givecard__batch__campaign=OuterRef("pk")
                    ).values("amount_value"),
                    sum_field="amount_value",
                    output_field=IntegerField(),
                ),
            )
        )

    def aggregate_total_amount_donated(self, hide_archived_batches=False) -> dict:
        """
        Returns the amount of $ users have donated with Givecards from all Campaigns in this QS
        This does not take into account any automatic donations
        """
        return (
            self.annotate_total_amount_donated(hide_archived_batches).aggregate(
                aggr_total_amount_donated=Sum("total_amount_donated")
            )["aggr_total_amount_donated"]
            or 0
        )

    def aggregate_sum_lives_impacted(self, hide_archived_batches=False):
        """Returns the amount of unique projects' Lives Impacted with Givecards from Campaigns in this QS"""
        filters = Q()
        if hide_archived_batches is True:
            filters |= Q(archived=False)
        return (
            self.filter(filters)
            .annotate(
                sum_lives_impacted=CoalesceZero(
                    SQSum(
                        Product.objects.filter(
                            purchase_report_data__givecard__batch__campaign__pk__in=self.values_list("pk", flat=True)
                        )
                        .values("pk")
                        .distinct()  # Get distinct products
                        .annotate(lives_impacted=F("project_extra__lives_impacted")),  # Simply annotate lives_impacted
                        sum_field="lives_impacted",
                    ),
                )
            )
            .values("sum_lives_impacted")
            .first()
        )["sum_lives_impacted"] or 0

    def _base_continued_giving(self, hide_archived_batches, campaign_q: Q):
        """
        Annotates four fields to campaigns in given queryset.

        The sum of all campaigns "Continued Giving" will end up being more
        than actually has been donated, because donated amounts will be counted
        towards all Campaigns user has previously redeemed Givecards from.
        This is the intended behaviour.

        continued_givers:
            The amount of people who have redeemed a Givecard from this campaign,
            and later donated any amount to any project using Stripe

        continued_giving:
            The total amount of money donated to projects by "Continued Givers"

        off_platform_donated:
            Sum of off-platform donations user has logged
        off_platform_hours:
            Sum of off-platform hours user has logged
        """

        from givesome.models import OffPlatformDonation, VolunteerHours

        filters = Q()
        if hide_archived_batches is True:
            filters |= Q(batch__archived=False)

        stripe_payment_method = PaymentMethod.objects.filter(
            payment_processor=StripeMultivendorPaymentProcessor.objects.filter(enabled=True).first()
        ).first()

        # All orders made using Stripe
        stripe_orders_subquery = Order.objects.filter(
            orderer__user=OuterRef("pk"),
            payment_method=stripe_payment_method,
            order_date__gt=OuterRef("first_redemption"),
        )

        def _get_users_first_givecard_redemption_subquery():
            """User QS with the the date they first redeemed a Givecard from this campaign annotated"""
            return User.objects.filter(campaign_q).annotate(
                first_redemption=Subquery(
                    Givecard.objects.filter(
                        filters,
                        user=OuterRef("pk"),
                    )
                    .order_by("redeemed_on")
                    .values("redeemed_on")[:1]
                )
            )

        def _get_continued_giver_users_subquery():
            """All users who have donated with Stripe after redeeming a Givecard from this Campaign"""
            return (
                _get_users_first_givecard_redemption_subquery()
                .annotate(
                    last_donation=Subquery(stripe_orders_subquery.order_by("-order_date").values("order_date")[:1]),
                )
                .filter(first_redemption__lt=F("last_donation"))
            )

        def _get_continued_givers():
            return CoalesceZero(
                SQCount(_get_continued_giver_users_subquery()),
            )

        def _get_continued_giving():
            return CoalesceZero(
                SQSum(
                    _get_continued_giver_users_subquery()
                    .annotate(
                        user_donations_sum=SQSum(
                            stripe_orders_subquery.values("taxless_total_price_value"),
                            sum_field="taxless_total_price_value",
                            output_field=IntegerField(),
                        )
                    )
                    .values("user_donations_sum"),
                    sum_field="user_donations_sum",
                    output_field=IntegerField(),
                ),
            )

        def _get_off_platform(off_platform_class, date_field: str, sum_field: str):
            return CoalesceZero(
                SQSum(
                    _get_users_first_givecard_redemption_subquery()
                    .annotate(
                        # The last time user
                        last_off_platform_event=Subquery(
                            off_platform_class.objects.filter(donor__user=OuterRef("pk"))
                            .order_by(f"-{date_field}")
                            .values(date_field)[:1]
                        ),
                        total_sum_field=SQSum(
                            off_platform_class.objects.filter(donor__user=OuterRef("pk")).values(sum_field),
                            sum_field=sum_field,
                            output_field=IntegerField(),
                        ),
                    )
                    .filter(first_redemption__lt=F("last_off_platform_event")),
                    sum_field="total_sum_field",
                    output_field=IntegerField(),
                ),
            )

        return self.annotate(
            continued_givers=_get_continued_givers(),
            continued_giving=_get_continued_giving(),
            off_platform_hours=_get_off_platform(VolunteerHours, "volunteered_on", "hours"),
            off_platform_donated=_get_off_platform(OffPlatformDonation, "donated_on", "amount"),
        )

    def annotate_continued_giving(self, hide_archived_batches=False):
        campaign_q = Q(givecards__batch__campaign_id=OuterRef("pk"))
        return self._base_continued_giving(hide_archived_batches, campaign_q)

    def aggregate_continued_giving(self, hide_archived_batches=False):
        """
        Annotate to all campaigns in `self` the sum of "continued fields".
        Then simply take the sum value from the first campaign.
        """
        campaign_q = Q(givecards__batch__campaign_id__in=self.values("pk"))
        return (
            self._base_continued_giving(hide_archived_batches, campaign_q)
            .values("continued_givers", "continued_giving", "off_platform_donated", "off_platform_hours")
            .first()
        )


class GivecardCampaign(TranslatableModel):
    created_on = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_("created on"))
    identifier = InternalIdentifierField(unique=True, editable=True)
    supplier = models.ForeignKey(
        "shuup.Supplier",
        related_name="campaigns",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("branded vendor"),
        help_text=_(
            "This Givecard Campaign and all givecards related to it will be "
            "available for selected vendor to be queried in reports."
        ),
    )
    translations = TranslatedFields(
        name=models.CharField(max_length=64),
        message=models.TextField(
            blank=True,
            null=True,
            max_length=500,
            verbose_name=_("Message"),
            help_text=_("Add a message to be shown to donors when they redeem a Givecard belonging to this campaign."),
        ),
    )
    image = FilerImageField(
        related_name="image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("image"),
        help_text=_("Add an image to be shown to donors when they redeem a Givecard belonging to this campaign."),
    )
    group = models.ForeignKey(
        "givesome.GivesomeGroup",
        related_name="campaigns",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Group"),
        help_text=_(
            "This is used to group Campaigns to different groups in the Vendor Dashboard, with their own subtotals"
        ),
    )
    archived = models.BooleanField(
        default=False,
        verbose_name=_("Archived"),
        help_text=_("Archived Givecard Campaigns are hidden on Vendor dashboards."),
    )

    objects = GivecardCampaignQuerySet.as_manager()

    class Meta:
        verbose_name_plural = _("givecard campaigns")

    def __str__(self):
        return f"{self.name}"

    def get_image_thumbnail(self, **kwargs):
        """
        Get thumbnail for image.

        This will return `None` if there is no file or kind is not `ProductMediaKind.IMAGE`

        :rtype: easy_thumbnails.files.ThumbnailFile|None
        """
        kwargs.setdefault("size", (64, 64))
        kwargs.setdefault("crop", False)  # sane defaults
        kwargs.setdefault("upscale", True)  # sane defaults

        if kwargs["size"] == (0, 0):
            return None

        if self.image is None:
            return None

        thumbnailer = get_thumbnailer(self.image)

        return thumbnailer.get_thumbnail(thumbnail_options=kwargs)

    def clean(self):
        self.clean_identifier()

    def clean_identifier(self):
        if not self.identifier:
            raise ValidationError(_("Givecard Campaign identifier is required"))
        if GivecardCampaign.objects.filter(identifier=self.identifier).exclude(pk=self.pk).exists():
            raise ValidationError("A Givecard Campaign with that identifier already exists")

    def get_projects_donated_to(self):
        return Product.objects.filter(purchase_report_data__givecard__batch__in=self.batches.all()).distinct()

    @property
    def sum_lives_impacted(self):
        return (
            self.get_projects_donated_to().aggregate(sum_lives_impacted=Sum("project_extra__lives_impacted"))[
                "sum_lives_impacted"
            ]
            or 0
        )


class GivesomeGroup(ShuupModel):
    """Givecard Campaign Group"""

    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

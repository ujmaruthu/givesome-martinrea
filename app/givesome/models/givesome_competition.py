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
from django.db.models import (
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Sum,
)
from django.db.models.functions import Cast
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from filer.fields.image import FilerImageField
from parler.models import TranslatableModel, TranslatedFields
from shuup.core.fields import InternalIdentifierField
from shuup.core.models import Order, Payment, PaymentMethod, Product, ShuupModel
from shuup_stripe_multivendor.models import StripeMultivendorPaymentProcessor

from givesome.admin_module.utils import CoalesceZero, SQCount, SQSum


class GivesomeCompetition(ShuupModel):
    created_on = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_("created on")
    )

    start_date = models.DateTimeField(
        editable=True,
        verbose_name=_("starting"),
        help_text=_("Start date of the competition"),
    )

    end_date = models.DateTimeField(
        editable=True,
        verbose_name=_("ending"),
        help_text=_("End date of the competition"),
    )

    slug = models.SlugField(
        help_text=_("Name of competition"), max_length=128, unique=True
    )

    competition_runner = models.ForeignKey(
        "shuup.Supplier",
        blank=True,
        help_text=_("The vendor running the competition"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="competition_runner",
        verbose_name=_("Competition Runner"),
    )

    competitors = models.ManyToManyField(
        User,
        related_name="competitors",
        blank=True,
        help_text=_(
            (
                "Add competitors here "
                "(competitors can also join if you give them the key / "
                "link to the competition)"
            )
        ),
    )

    active = models.BooleanField(
        default=True,
        verbose_name=_("active"),
        help_text=_("Is this competition active?"),
    )

    competition_key = models.CharField(
        max_length=64, help_text=_("Key for customers to enter competition")
    )

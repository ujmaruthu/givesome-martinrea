# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from parler.models import TranslatableModel, TranslatedFields
from shuup.core.fields import InternalIdentifierField
from shuup.core.models import ShuupModel
from shuup.utils.analog import define_log_model


class SustainabilityGoal(TranslatableModel):
    identifier = InternalIdentifierField(unique=False, editable=True)
    translations = TranslatedFields(
        name=models.CharField(
            max_length=64,
            verbose_name=_("name"),
            help_text=_("You can choose up to three Sustainable Development Goals (SDGs)."),
        ),
        description=models.CharField(
            max_length=128, verbose_name=_("description"), help_text=_("Describe the SDG to your potential donors.")
        ),
    )
    image = FilerImageField(
        verbose_name=_("image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_("Supply an image to illustrate the SDG to your potential donors."),
        related_name="sdg_images",
    )

    def __str__(self):
        return force_text(self.safe_translation_getter("name") or self.identifier)


SustainabilityGoalLogEntry = define_log_model(SustainabilityGoal)


class VendorSustainabilityGoals(ShuupModel):
    vendor = models.OneToOneField(
        "shuup.Supplier", related_name="vendor_sustainability_goals", on_delete=models.CASCADE
    )
    goals = models.ManyToManyField(
        SustainabilityGoal, blank=True, related_name="vendor_sustainability_goals", verbose_name=_("vendors")
    )

    def __str__(self):
        return f"Vendor {self.vendor.name} SDGs"


class ProjectSustainabilityGoals(ShuupModel):
    project = models.OneToOneField(
        "shuup.ShopProduct", related_name="project_sustainability_goals", on_delete=models.CASCADE
    )
    goals = models.ManyToManyField(
        SustainabilityGoal, blank=True, related_name="project_sustainability_goals", verbose_name=_("projects")
    )

    def __str__(self):
        return f"Project {self.project} SDGs"


class OfficeSustainabilityGoals(ShuupModel):
    office = models.OneToOneField(
        "givesome.GivesomeOffice", related_name="office_sustainability_goals", on_delete=models.CASCADE
    )
    goals = models.ManyToManyField(
        SustainabilityGoal, blank=True, related_name="office_sustainability_goals", verbose_name=_("offices")
    )

    def __str__(self):
        return f"Office {self.office.name} SDGs"

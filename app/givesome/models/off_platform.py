from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class VolunteerHours(models.Model):
    donor = models.ForeignKey("shuup.PersonContact", on_delete=models.PROTECT, related_name="volunteer_hours")
    hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("How many hours did you volunteer?"),
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Hours"),
    )
    volunteered_on = models.DateField(help_text=_("When did you volunteer?"), verbose_name=_("Volunteered on"))
    description = models.CharField(
        max_length=68, help_text=_("Who did you help?"), verbose_name=_("Where did you volunteer?")
    )


class OffPlatformDonation(models.Model):
    donor = models.ForeignKey("shuup.PersonContact", on_delete=models.PROTECT, related_name="off_platform_donations")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("How much did you donate?"),
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Amount"),
    )
    donated_on = models.DateField(help_text=_("When did you donate?"), verbose_name=_("Donated on"))
    description = models.CharField(
        max_length=68, help_text=_("Who did you help?"), verbose_name=_("Where did you give to?")
    )

from django.db import models
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField


class GivesomeGif(models.Model):
    gif = FilerImageField(
        verbose_name=_("gif"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_("Gif that can be displayed on the checkout competion."),
    )
    active = models.BooleanField(db_index=True, default=True, verbose_name=_("active"))

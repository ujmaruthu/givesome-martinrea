# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django.db import models

from shuup.core.fields import SeparatedValuesField


class FieldsModel(models.Model):
    separated_values = SeparatedValuesField(blank=True)
    separated_values_semi = SeparatedValuesField(blank=True, separator=";")
    separated_values_dash = SeparatedValuesField(blank=True, separator="-")

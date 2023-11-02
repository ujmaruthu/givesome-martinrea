# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import absolute_import

from django import forms
from django.core.validators import FileExtensionValidator, validate_image_file_extension
from django.utils.translation import ugettext as _

from shuup import configuration
from shuup.core.setting_keys import SHUUP_ALLOWED_UPLOAD_EXTENSIONS
from shuup.utils.filer import file_name_size_validator, file_size_validator


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label=_("Upload File"),
        validators=[
            FileExtensionValidator(allowed_extensions=configuration.get(None, SHUUP_ALLOWED_UPLOAD_EXTENSIONS)),
            file_size_validator,
            file_name_size_validator,
        ],
    )


class UploadImageForm(forms.Form):
    file = forms.ImageField(
        label=_("Upload Image"),
        validators=[validate_image_file_extension, file_size_validator, file_name_size_validator],
    )

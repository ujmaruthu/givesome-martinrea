# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from django.http.response import HttpResponseForbidden, JsonResponse
from django.utils.translation import ugettext_lazy as _

from shuup import configuration
from shuup.core.shop_provider import get_shop
from shuup.front.setting_keys import SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD, SHUUP_FRONT_MAX_UPLOAD_SIZE
from shuup.utils.filer import (
    ensure_media_file,
    file_name_size_validator,
    filer_file_to_json_dict,
    filer_image_from_upload,
    get_or_create_folder,
)


def file_size_validator(value):
    size = getattr(value, "size", None)
    front_max_upload_size = configuration.get(None, SHUUP_FRONT_MAX_UPLOAD_SIZE)
    if size and front_max_upload_size and front_max_upload_size < size:
        raise ValidationError(
            _("Maximum file size reached (%(size)s MB).") % {"size": front_max_upload_size / 1000 / 1000},
            code="file_max_size_reached",
        )

    return value


class UploadImageForm(forms.Form):
    file = forms.ImageField(validators=[file_size_validator, validate_image_file_extension, file_name_size_validator])


def media_upload(request, *args, **kwargs):
    if not configuration.get(None, SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD):
        return HttpResponseForbidden()

    shop = get_shop(request)
    folder = get_or_create_folder(shop, "/contacts")
    form = UploadImageForm(request.POST, request.FILES)
    if form.is_valid():
        filer_file = filer_image_from_upload(request, path=folder, upload_data=request.FILES["file"])
    else:
        error_messages = []
        for validation_error in form.errors.as_data().get("file", []):
            error_messages += validation_error.messages

        return JsonResponse({"error": ", ".join([msg for msg in error_messages])}, status=400)

    ensure_media_file(shop, filer_file)
    return JsonResponse({"file": filer_file_to_json_dict(filer_file)})

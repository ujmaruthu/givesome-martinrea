# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.forms.models import ModelForm
from filer.fields.file import AdminFileWidget

from shuup.admin.forms.widgets import FileDnDUploaderWidget
from shuup.utils.multilanguage_model_form import MultiLanguageModelForm


class ShuupAdminForm(MultiLanguageModelForm):
    def __init__(self, **kwargs):
        super(ShuupAdminForm, self).__init__(**kwargs)
        for field in self.fields:
            if issubclass(self.fields[field].widget.__class__, AdminFileWidget):
                self.fields[field].widget = FileDnDUploaderWidget(upload_path="/default", kind="images", clearable=True)


class ShuupAdminFormNoTranslation(ModelForm):
    def __init__(self, **kwargs):
        super(ShuupAdminFormNoTranslation, self).__init__(**kwargs)
        for field in self.fields:
            if issubclass(self.fields[field].widget.__class__, AdminFileWidget):
                self.fields[field].widget = FileDnDUploaderWidget(upload_path="/default", kind="images", clearable=True)

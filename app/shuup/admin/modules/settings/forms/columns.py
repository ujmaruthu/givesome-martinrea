# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django import forms


class ColumnSettingsForm(forms.Form):
    settings = None
    non_selected = []
    selected = []

    def __init__(self, settings, *args, **kwargs):
        super(ColumnSettingsForm, self).__init__(*args, **kwargs)
        self.settings = settings
        self.selected = [settings.get_settings_key(c.id) for c in settings.active_columns]
        self.non_selected = [settings.get_settings_key(c.id) for c in settings.inactive_columns]

        for column in settings.column_spec:
            settings_key = settings.get_settings_key(column.id)
            self.fields[settings_key] = forms.BooleanField(label=column.title, required=False)

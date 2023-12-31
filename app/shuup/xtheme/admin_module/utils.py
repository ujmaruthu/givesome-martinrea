# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from shuup.apps.provides import get_provide_objects
from shuup.xtheme.models import ThemeSettings


def get_theme_context(shop):
    themes = []
    active_theme = None

    # create one ThemeSettings for each theme if needed
    for theme in get_provide_objects("xtheme"):
        if not theme.identifier:
            continue

        theme_settings = ThemeSettings.objects.get_or_create(theme_identifier=theme.identifier, shop=shop)[0]
        themes.append(theme)

        if theme_settings.active:
            active_theme = theme

    return {"theme_classes": sorted(themes, key=lambda t: (t.name or t.identifier)), "current_theme": active_theme}

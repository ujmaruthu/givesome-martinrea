# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from shuup.xtheme.admin_module.views._snippet import SnippetDeleteView, SnippetEditView, SnippetListView
from shuup.xtheme.admin_module.views._theme import (
    ActivationForm,
    AdminThemeConfigDetailView,
    AdminThemeForm,
    FontEditView,
    FontForm,
    FontListView,
    TemplateView,
    ThemeConfigDetailView,
    ThemeConfigView,
    ThemeGuideTemplateView,
    ThemeWizardPane,
)

__all__ = [
    "ActivationForm",
    "FontEditView",
    "AdminThemeForm",
    "AdminThemeConfigDetailView",
    "FontForm",
    "FontListView",
    "SnippetDeleteView",
    "SnippetEditView",
    "SnippetListView",
    "TemplateView",
    "ThemeConfigDetailView",
    "ThemeConfigView",
    "ThemeGuideTemplateView",
    "ThemeWizardPane",
]

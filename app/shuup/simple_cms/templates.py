# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _


class SimpleCMSDefaultTemplate(object):
    name = _("Default Page")
    template_path = "shuup/simple_cms/page.jinja"


class SimpleCMSTemplateSidebar(object):
    name = _("Page with sidebar")
    template_path = "shuup/simple_cms/page_sidebar.jinja"

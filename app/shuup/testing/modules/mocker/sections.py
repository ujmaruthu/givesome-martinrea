# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import Section


class MockContactSection(Section):
    identifier = "contact_mock_section"
    name = _("mock section title")
    icon = "fa-globe"
    template = "shuup_testing/_contact_mock_section.jinja"
    order = 9

    @classmethod
    def visible_for_object(cls, contact, request=None):
        return True

    @classmethod
    def get_context_data(cls, contact, request=None):
        context = {}
        context["mock_context"] = "mock section context data"
        return context

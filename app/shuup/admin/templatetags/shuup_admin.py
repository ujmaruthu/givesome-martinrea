# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from bootstrap3.renderers import FormRenderer
from django.utils.safestring import mark_safe
from django_jinja import library

from shuup.admin.template_helpers import shuup_admin as shuup_admin_template_helpers
from shuup.admin.utils.bs3_renderers import AdminFieldRenderer


class Bootstrap3Namespace(object):
    def field(self, field, **kwargs):
        if not field:
            return ""
        return mark_safe(AdminFieldRenderer(field, **kwargs).render())

    def form(self, form, **kwargs):
        return mark_safe(FormRenderer(form, **kwargs).render())


library.global_function(name="shuup_admin", fn=shuup_admin_template_helpers)
library.global_function(name="bs3", fn=Bootstrap3Namespace())

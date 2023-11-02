# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

import django.core.serializers.json
from django.utils.functional import Promise

from shuup.utils.django_compat import force_text


class ExtendedJSONEncoder(django.core.serializers.json.DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_text(o)
        return super(ExtendedJSONEncoder, self).default(o)

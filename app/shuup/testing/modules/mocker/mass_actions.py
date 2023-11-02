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

from shuup.admin.utils.picotable import PicotableMassAction, PicotableMassActionProvider


class DummyPicotableMassAction1(PicotableMassAction):
    label = _("Dummy Mass Action #1")
    identifier = "dummy_mass_action_1"


class DummyPicotableMassAction2(PicotableMassAction):
    label = _("Dummy Mass Action #2")
    identifier = "dummy_mass_action_2"


class DummyMassActionProvider(PicotableMassActionProvider):
    @classmethod
    def get_mass_actions_for_view(cls, view):
        return [
            "shuup.testing.modules.mocker.mass_actions:DummyPicotableMassAction1",
            "shuup.testing.modules.mocker.mass_actions:DummyPicotableMassAction2",
        ]

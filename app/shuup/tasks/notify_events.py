# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.notify.base import Event, Variable
from shuup.notify.typology import Enum, Integer, Model, Text
from shuup.tasks.models import TaskStatus


class TaskCreated(Event):
    identifier = "task_created"
    name = _("Task Created")

    task = Variable(_("Task"), type=Text)
    type = Variable(_("Type"), type=Model("shuup_tasks.TaskType"))
    status = Variable(_("Status"), type=Enum(TaskStatus))
    priority = Variable(_("Priority"), type=Integer)

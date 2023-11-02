# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db.transaction import atomic

from shuup.tasks.notify_events import TaskCreated


def create_task(shop, creator, task_type, task_name, comment=None, **kwargs):
    from shuup.tasks.models import Task

    with atomic():
        task = Task(creator=creator, shop=shop, type=task_type, name=task_name, **kwargs)
        task.full_clean()
        task.save()
        if comment:
            task.comment(creator, comment)

        params = dict(
            type=task_type,
            task=task_name,
            status=task.status,
            priority=task.priority,
        )
        TaskCreated(**params).run(shop)
        return task

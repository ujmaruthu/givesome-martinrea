# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.tasks"
    label = "shuup_tasks"
    provides = {
        "admin_module": ["shuup.tasks.admin_module.TaskAdminModule", "shuup.tasks.admin_module.TaskTypeAdminModule"]
    }

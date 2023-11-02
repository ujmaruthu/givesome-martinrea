# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.reports"
    label = "shuup_reports"
    verbose_name = "Shuup Reports"
    provides = {
        "admin_module": ["shuup.reports.admin_module:ReportsAdminModule"],
        "report_writer_populator": ["shuup.reports.writer.populate_default_writers"],
        "system_settings_form_part": [
            "shuup.reports.admin_module.setting_form.ReportSettingsFormPart",
        ],
        "system_setting_keys": [
            "shuup.reports.setting_keys",
        ],
    }

    def ready(self):

        # connect signals
        import shuup.reports.signal_handlers  # noqa: F401

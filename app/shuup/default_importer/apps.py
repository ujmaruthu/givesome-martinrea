# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.default_importer"
    provides = {
        "importers": [
            "shuup.default_importer.importers.ProductImporter",
            "shuup.default_importer.importers.PersonContactImporter",
            "shuup.default_importer.importers.CompanyContactImporter",
        ],
    }

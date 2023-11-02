# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.management.base import BaseCommand

from shuup.core.catalog.utils import reindex_all_shop_products


class Command(BaseCommand):
    help = "Reindex the prices and availability of all products of the catalog"

    def handle(self, *args, **options):
        reindex_all_shop_products()

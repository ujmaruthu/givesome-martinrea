# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.management.base import BaseCommand

from shuup.core.signals import shuup_deployed


class Command(BaseCommand):
    help = (
        "This command should be triggered after Shuup is sucessfully deployed "
        "and after the app is reloaded in the server. "
        "The command will just trigger the `shuup_deployed` "
        "signal that apps can listed and do additional setup and/or configuration."
    )

    def handle(self, *args, **options):
        shuup_deployed.send(sender=type(self))

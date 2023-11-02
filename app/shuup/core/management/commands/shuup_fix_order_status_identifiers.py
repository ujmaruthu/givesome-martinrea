# This file is part of Shuup.
#
# Copyright (c) 2017, Anders Innovations. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from shuup.core.models import OrderStatus, OrderStatusRole


class Command(BaseCommand):
    @atomic
    def handle(self, *args, **options):
        data = [  # role, invalid_identifier, valid_identifier
            (OrderStatusRole.PROCESSING, "canceled", "processing"),
            (OrderStatusRole.COMPLETE, "processing", "complete"),
            (OrderStatusRole.CANCELED, "complete", "canceled"),
        ]

        to_post_process = []

        for (role, invalid_identifier, valid_identifier) in data:
            status = OrderStatus.objects.filter(identifier=invalid_identifier, role=role).first()
            if not status:
                self.stdout.write("No changes to {} statuses".format(role))
                continue
            tmp_identifier = valid_identifier + "_tmp"
            self.stdout.write(
                "Updating identifier of {} status: {!r} -> {!r}".format(role, status.identifier, tmp_identifier)
            )
            status.identifier = tmp_identifier
            status.save()
            to_post_process.append(status)

        for status in to_post_process:
            new_identifier = status.identifier.replace("_tmp", "")
            self.stdout.write(
                "Updating identifier of {} status: {!r} -> {!r}".format(status.role, status.identifier, new_identifier)
            )
            status.identifier = new_identifier
            status.save()

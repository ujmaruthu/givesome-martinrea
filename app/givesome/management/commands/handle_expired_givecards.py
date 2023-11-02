# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.management import BaseCommand
from django.db.models import F
from django.utils import timezone
from shuup.core.models import ShopProduct, Supplier

from givesome.enums import GivecardBatchExpiryType, GivesomeDonationType
from givesome.models import (
    GivecardBatch,
    GivecardBatchQuerySet,
    GivecardPurseCharge,
    GivesomeDonationData,
    GivesomeOffice,
    GivesomePurse,
)
from givesome.models.givesome_purse import create_order_for_donation


def _log_order_data(order, batch, donate_source=None, donation_method=""):
    if order is not None:
        is_office = issubclass(donate_source.__class__, GivesomeOffice)
        is_supplier = issubclass(donate_source.__class__, Supplier)

        donation_type = None
        if donation_method == "primary":
            donation_type = GivesomeDonationType.OFFICE_PRIMARY if is_office else GivesomeDonationType.BRAND_PRIMARY
        elif donation_method == "promoted":
            donation_type = GivesomeDonationType.OFFICE_PROMOTED if is_office else GivesomeDonationType.BRAND_PROMOTED

        GivesomeDonationData.objects.create(
            supplier=donate_source if is_supplier else None,
            office=donate_source if is_office else None,
            batch=batch,
            payment=order.payments.first(),
            donation_type=donation_type,
        )


class Command(BaseCommand):
    @staticmethod
    def donate_to_single_project(batch: GivecardBatch, project: ShopProduct, donate_source=None):
        """
        Expend all balance from batch's Givecards until
        balance runs out or project becomes fully funded
        """
        if project is None:
            return

        order_comment = "Expired Givecard Automatic Donation"
        if donate_source is not None:
            order_comment += f" ({donate_source.name}'s Primary Project)"
        payment_comment = f"Expired Givecard Batch {batch.pk} Automatic Donation"

        givecards = batch.givecards.filter(balance__gt=0)
        progress_left = project.product.project_extra.funding_required
        total_donated = 0
        for givecard in givecards:
            if progress_left == 0:
                break

            donate_amount = min(progress_left, givecard.balance)
            progress_left = progress_left - donate_amount
            total_donated = total_donated + donate_amount
            givecard.balance = givecard.balance - donate_amount
            givecard.automatically_donated = donate_amount
            givecard.save()

        order = create_order_for_donation(project, total_donated, order_comment, payment_comment)
        _log_order_data(order, batch, donate_source, "primary")

    @staticmethod
    def donate_to_multiple_projects_equally(batch: GivecardBatch, projects, donate_source=None):
        """
        Expend all balance from batch's Givecards until
        balance runs out or all projects becomes fully funded

        Goal is to distribute funds as evenly as possible
        so balance is distributed $1 at a time
        """
        order_comment = "Expired Givecard Automatic Donation"
        if donate_source is not None:
            order_comment += f" ({donate_source.name}'s Promoted Project)"
        payment_comment = f"Expired Givecard Batch {batch.pk} Automatic Donation"

        projects = projects.filter(product__simple_supplier_stock_count__logical_count__gt=0).prefetch_related(
            "product", "product__project_extra"
        )
        project_data = [
            {
                "project": project,
                "progress_left": project.product.project_extra.funding_required,
                "total_donated": 0,
            }
            for project in projects
        ]
        givecards = batch.givecards.filter(balance__gt=0)

        if len(project_data) == 0:
            return

        last_project = 0  # Keeps track of which project's donation was added last
        for givecard in givecards:
            while givecard.balance > 0:  # Fully reallocate Givecards balance
                last_project = (last_project + 1) % len(project_data)  # Loop through projects
                if project_data[last_project]["progress_left"] == 0:  # This project is fully funded
                    if all([project["progress_left"] == 0 for project in project_data]):  # All projects fully funded
                        givecard.save()  # In case givecard was partially used
                        for project in project_data:  # Donate to projects
                            order = create_order_for_donation(
                                project["project"], project["total_donated"], order_comment, payment_comment
                            )
                            _log_order_data(order, batch, donate_source, "promoted")
                        return  # All projects fully funded and donate to
                    continue  # Project fully funded, continue to next
                project_data[last_project]["progress_left"] = project_data[last_project]["progress_left"] - 1
                project_data[last_project]["total_donated"] = project_data[last_project]["total_donated"] + 1
                givecard.balance = givecard.balance - 1
                givecard.automatically_donated = givecard.automatically_donated + 1
            givecard.save()  # Givecard balance distributed
        for project in project_data:  # Givecard Batch balance ran out, donate funds
            order = create_order_for_donation(
                project["project"], project["total_donated"], order_comment, payment_comment
            )
            _log_order_data(order, batch, donate_source, "promoted")

    def handle_office_primary_project(self, batch: GivecardBatch):
        """Donate to GivecardBatch's balance to office's primary project"""
        if batch.office is not None:
            self.donate_to_single_project(batch, batch.office.primary_project, batch.office)
        if batch.office.parent is not None:
            for office in batch.office.get_ancestors(ascending=True):  # Immediate parents first
                self.donate_to_single_project(batch, office.primary_project, office)

    def handle_supplier_primary_project(self, batch: GivecardBatch):
        """Donate to GivecardBatch's balance to supplier's primary project"""
        if batch.supplier is not None and batch.supplier.givesome_extra is not None:
            self.donate_to_single_project(batch, batch.supplier.givesome_extra.primary_project, batch.supplier)

    def handle_office_promoted_projects(self, batch: GivecardBatch):
        """Donate to GivecardBatch's balance to office's promoted projects"""
        if batch.office is not None:
            projects = ShopProduct.objects.filter(promotions__office=batch.office)
            self.donate_to_multiple_projects_equally(batch, projects, batch.office)
        if batch.office.parent is not None:
            for office in batch.office.get_ancestors(ascending=True):  # Immediate parents first
                projects = ShopProduct.objects.filter(promotions__office=office)
                self.donate_to_multiple_projects_equally(batch, projects, office)

    def handle_supplier_promoted_projects(self, batch: GivecardBatch):
        """Donate to GivecardBatch's balance to supplier's promoted projects"""
        if batch.supplier is not None and batch.supplier.givesome_extra is not None:
            projects = ShopProduct.objects.filter(promotions__supplier=batch.supplier)
            self.donate_to_multiple_projects_equally(batch, projects, batch.supplier)

    def handle_automatic_batches(self, batches: GivecardBatchQuerySet):
        for batch in batches.has_balance().filter(office__isnull=False):
            self.handle_office_primary_project(batch)

        for batch in batches.has_balance().filter(supplier__isnull=False):
            self.handle_supplier_primary_project(batch)

        for batch in batches.has_balance().filter(office__isnull=False):
            self.handle_office_promoted_projects(batch)

        for batch in batches.has_balance().filter(supplier__isnull=False):
            self.handle_supplier_promoted_projects(batch)

    @staticmethod
    def handle_manual_batches(batches: GivecardBatchQuerySet):
        def _create_purse_charge(batch, purse):
            GivecardPurseCharge.objects.create(
                purse=purse,
                batch=batch,
                charge_amount=batch.total_balance,
                charge_date=timezone.localtime(),
            )
            batch.givecards.update(automatically_donated=F("balance"), balance=0)

        # Batches whose suppliers are allowed a Purse
        for batch in batches.has_balance().filter(supplier__isnull=False, supplier__givesome_extra__allow_purse=True):
            purse = GivesomePurse.objects.get(supplier=batch.supplier)
            _create_purse_charge(batch, purse)

        # Everything else goes to Givesome's own Purse
        purse = GivesomePurse.objects.filter(supplier=None).first()
        if purse is not None:  # Should always exist, but don't fail hard in case it doesn't (e.g. in tests)
            for batch in batches.has_balance():
                _create_purse_charge(batch, purse)

    def handle(self, *args, **options):
        expiredBatches = GivecardBatch.objects.expired()

        # Automatically donate funds to projects
        self.handle_automatic_batches(expiredBatches.filter(expiry_type=GivecardBatchExpiryType.AUTOMATIC))

        # Transfer funds to Givesome or Brand purses
        # Both MANUAL and any leftover funds from AUTOMATIC Batches are transferred
        self.handle_manual_batches(expiredBatches.exclude(expiry_type=GivecardBatchExpiryType.DISABLED))

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone
from shuup.core.defaults.order_statuses import create_default_order_statuses
from shuup.core.models import Order, PaymentStatus, ShopProduct

from givesome.models import GivesomePromotedProduct
from givesome_tests.factories import get_default_purse, givecard_batch_factory, givecard_campaign_factory
from givesome_tests.utils import (
    create_layers_of_offices,
    create_offices_primary_projects,
    create_offices_promote_projects,
)


def change_project_goal(project: ShopProduct, amount: int):
    project.product.project_extra.goal_amount = amount
    project.product.project_extra.save()
    project.suppliers.first().adjust_stock(project.id, amount - 1000)


@pytest.mark.django_db
def test_expiry_reallocate_funds_to_office_primary_project(vendor_user_brand, vendor_user_charity):
    create_default_order_statuses()
    create_offices_primary_projects(vendor_user_brand, vendor_user_charity)
    create_offices_promote_projects(vendor_user_brand, vendor_user_charity)
    project = vendor_user_charity.project
    batch = givecard_batch_factory(
        amount=100,
        value=10,
        campaign=givecard_campaign_factory(),
        supplier=vendor_user_brand.vendor,
        office=vendor_user_brand.office,
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
    ).generate_givecards()
    # End of setup

    call_command("handle_expired_givecards")

    assert batch.total_balance == 0  # Completely donated to project
    assert project.product.project_extra.goal_amount == 1000  # Goal is always $1000
    assert project.product.project_extra.goal_progress_amount == 1000  # Balance transferred to project
    assert Order.objects.count() == 1  # There should be only one donation order
    assert Order.objects.get(pk=1).payment_status == PaymentStatus.FULLY_PAID  # Order is fully paid
    assert Order.objects.get(pk=1).is_complete()


@pytest.mark.django_db
def test_expiry_reallocate_funds_to_supplier_primary_project(vendor_user_brand, vendor_user_charity):
    create_default_order_statuses()
    create_offices_primary_projects(vendor_user_brand, vendor_user_charity)
    brand_vendor = vendor_user_brand.vendor
    project = vendor_user_charity.project
    brand_vendor.givesome_extra.primary_project = project
    brand_vendor.givesome_extra.save()
    batch = givecard_batch_factory(
        amount=1500,
        value=1,
        campaign=givecard_campaign_factory(),
        supplier=brand_vendor,
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
    ).generate_givecards()
    # End of setup

    call_command("handle_expired_givecards")

    assert batch.total_balance == 500  # 500 left over
    assert project.product.project_extra.goal_progress_amount == 1000  # Fully funded


@pytest.mark.django_db
def test_expiry_reallocate_funds_equally_office_promoted_projects(vendor_user_brand, vendor_user_charity):
    create_default_order_statuses()
    office = vendor_user_brand.office
    projects = vendor_user_charity.all_projects
    for project in projects:
        GivesomePromotedProduct.objects.create(office=office, shop_product=project)
    batch = givecard_batch_factory(
        amount=40,
        value=5,  # Funds can be distributed equally to all projects, $50 to each project
        campaign=givecard_campaign_factory(),
        supplier=vendor_user_brand.vendor,
        office=office,
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
    ).generate_givecards()
    # End of setup

    call_command("handle_expired_givecards")

    assert batch.total_balance == 0  # Completely donated to projects
    assert office.promoted_projects.count() == 4  # 4 promoted projects
    assert Order.objects.count() == 4  # One order for every project donated to
    assert vendor_user_charity.project.product.project_extra.goal_progress_amount == 50  # All projects
    assert vendor_user_charity.project2.product.project_extra.goal_progress_amount == 50  # have $50
    assert vendor_user_charity.project3.product.project_extra.goal_progress_amount == 50  # donated
    assert vendor_user_charity.project4.product.project_extra.goal_progress_amount == 50  # to them


@pytest.mark.django_db
def test_expiry_reallocate_funds_equally_office_projects_different_goal_amounts(vendor_user_brand, vendor_user_charity):
    create_default_order_statuses()
    office = vendor_user_brand.office
    projects = vendor_user_charity.all_projects
    for project in projects:
        GivesomePromotedProduct.objects.create(office=office, shop_product=project)
    change_project_goal(vendor_user_charity.project, 100)
    batch = givecard_batch_factory(
        amount=20,
        value=50,  # First project fully funded, rest is divided equally perfectly
        campaign=givecard_campaign_factory(),
        supplier=vendor_user_brand.vendor,
        office=office,
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
    ).generate_givecards()
    # End of setup

    call_command("handle_expired_givecards")

    assert batch.total_balance == 0  # Completely donated to projects
    assert office.promoted_projects.count() == 4  # 4 promoted projects
    assert Order.objects.count() == 4  # One order for every project donated to
    assert vendor_user_charity.project.product.project_extra.goal_amount == 100
    assert vendor_user_charity.project.product.project_extra.goal_progress_amount == 100  # Fully funded
    assert vendor_user_charity.project2.product.project_extra.goal_progress_amount == 300  # rest of the funds
    assert vendor_user_charity.project3.product.project_extra.goal_progress_amount == 300  # are divided equally
    assert vendor_user_charity.project4.product.project_extra.goal_progress_amount == 300  # to remaining projects


@pytest.mark.django_db
def test_expiry_reallocate_funds_equally_for_office_and_supplier_projects(vendor_user_brand, vendor_user_charity):
    create_default_order_statuses()
    office1 = vendor_user_brand.office
    office2 = vendor_user_brand.office2
    projects = [vendor_user_charity.project, vendor_user_charity.project2, vendor_user_charity.project3]
    # Office 1 promotes projects 1, 2, 3
    for project in projects:
        GivesomePromotedProduct.objects.create(office=office1, shop_product=project)
    # Office 2 promotes project 4
    GivesomePromotedProduct.objects.create(office=office2, shop_product=vendor_user_charity.project4)
    change_project_goal(vendor_user_charity.project, 500)
    batch = givecard_batch_factory(
        amount=30,
        value=100,  # Enough to fully fund projects 1,2,3 and half of 4
        campaign=givecard_campaign_factory(),
        supplier=vendor_user_brand.vendor,
        office=office1,
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
    ).generate_givecards()
    # End of setup

    call_command("handle_expired_givecards")

    assert batch.total_balance == 500
    assert office1.promoted_projects.count() == 3
    assert Order.objects.count() == 3  # One order for every project donated to
    assert vendor_user_charity.project.product.project_extra.goal_amount == 500
    assert vendor_user_charity.project.product.project_extra.goal_progress_amount == 500  # Fully funded
    assert vendor_user_charity.project2.product.project_extra.goal_progress_amount == 1000
    assert vendor_user_charity.project3.product.project_extra.goal_progress_amount == 1000
    # All projects by office were fully funded, Other offices promoted projects are not touched
    assert office2.promoted_projects.count() == 1
    assert vendor_user_charity.project4.product.project_extra.goal_progress_amount == 0


@pytest.mark.django_db
def test_expiry_everything_office_and_supplier_primary_and_promoted_projects(vendor_user_brand, vendor_user_charity):
    create_default_order_statuses()
    brand_vendor = vendor_user_brand.vendor
    office1 = vendor_user_brand.office
    GivesomePromotedProduct.objects.create(office=office1, shop_product=vendor_user_charity.project)
    GivesomePromotedProduct.objects.create(office=office1, shop_product=vendor_user_charity.project2)
    GivesomePromotedProduct.objects.create(supplier=brand_vendor, shop_product=vendor_user_charity.project3)
    GivesomePromotedProduct.objects.create(office=vendor_user_brand.office2, shop_product=vendor_user_charity.project4)
    office1.primary_project = vendor_user_charity.project
    office1.save()
    brand_vendor.givesome_extra.primary_project = vendor_user_charity.project4
    brand_vendor.givesome_extra.save()
    common_data = dict(
        value=100,
        campaign=givecard_campaign_factory(),
        supplier=brand_vendor,
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
    )
    batch1 = givecard_batch_factory(amount=30, office=office1, **common_data).generate_givecards()
    batch2 = givecard_batch_factory(amount=10, **common_data).generate_givecards()
    # End of setup

    call_command("handle_expired_givecards")

    # Batch 1 donates to Project 1 due to Office 1 having it as primary project
    assert vendor_user_charity.project.product.project_extra.goal_progress_amount == 1000  # Fully funded

    # Batch 2 donates to Project 4 due to Vendor having it as primary project
    assert vendor_user_charity.project4.product.project_extra.goal_progress_amount == 1000  # Fully funded
    assert batch2.total_balance == 0  # Completely donated to projects

    # Batch 1 donates to Project 2 due to it being promoted by Office 1
    assert vendor_user_charity.project2.product.project_extra.goal_progress_amount == 1000  # Fully funded

    # Batch 1 donates to Project 2 due to it being promoted by Vendor
    assert vendor_user_charity.project3.product.project_extra.goal_progress_amount == 1000  # Fully funded
    assert batch1.total_balance == 0  # Completely donated to projects


def _base_test_expiry_reallocate_funds_to_layers_of_offices(vendor_user_brand, vendor_user_charity):
    """
    Reallocate funds correctly using Layers of Offices
    Batch funds     Restriction |   Results
    Batch1 $500     Office1     =>  Project1 ($500/1000)
    Batch2 $1200    Office2     =>  Project2 ($1000/1000),  Project1 ($700/1000)
    Batch3 $1200    Office3     =>  Project3 ($1000/1000),  Project1 ($900/1000)
    """
    create_default_order_statuses()
    create_layers_of_offices(vendor_user_brand)

    common_data = dict(
        value=100,
        campaign=givecard_campaign_factory(),
        supplier=vendor_user_brand.vendor,
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
    )
    # End of setup

    batch1 = givecard_batch_factory(amount=5, office=vendor_user_brand.office, **common_data).generate_givecards()
    call_command("handle_expired_givecards")
    assert batch1.total_balance == 0
    assert vendor_user_charity.project.product.project_extra.goal_progress_amount == 500
    assert vendor_user_charity.project2.product.project_extra.goal_progress_amount == 0
    assert vendor_user_charity.project3.product.project_extra.goal_progress_amount == 0

    batch2 = givecard_batch_factory(amount=12, office=vendor_user_brand.office2, **common_data).generate_givecards()
    call_command("handle_expired_givecards")
    assert batch2.total_balance == 0
    assert vendor_user_charity.project.product.project_extra.goal_progress_amount == 700
    assert vendor_user_charity.project2.product.project_extra.goal_progress_amount == 1000
    assert vendor_user_charity.project3.product.project_extra.goal_progress_amount == 0

    batch3 = givecard_batch_factory(amount=12, office=vendor_user_brand.office3, **common_data).generate_givecards()
    call_command("handle_expired_givecards")
    assert batch3.total_balance == 0
    assert vendor_user_charity.project.product.project_extra.goal_progress_amount == 900
    assert vendor_user_charity.project2.product.project_extra.goal_progress_amount == 1000
    assert vendor_user_charity.project3.product.project_extra.goal_progress_amount == 1000


@pytest.mark.django_db
def test_expiry_reallocate_funds_to_layers_of_offices_primary_projects(vendor_user_brand, vendor_user_charity):
    create_offices_primary_projects(vendor_user_brand, vendor_user_charity)
    _base_test_expiry_reallocate_funds_to_layers_of_offices(vendor_user_brand, vendor_user_charity)


@pytest.mark.django_db
def test_expiry_reallocate_funds_to_layers_of_offices_promoted_projects(vendor_user_brand, vendor_user_charity):
    create_offices_promote_projects(vendor_user_brand, vendor_user_charity)
    _base_test_expiry_reallocate_funds_to_layers_of_offices(vendor_user_brand, vendor_user_charity)


@pytest.mark.django_db
def test_expiry_reallocate_funds_excess_funds_to_to_purse(vendor_user_brand, vendor_user_charity):
    create_default_order_statuses()
    purse = get_default_purse(supplier=vendor_user_brand.vendor)
    create_offices_primary_projects(vendor_user_brand, vendor_user_charity)
    project = vendor_user_charity.project
    batch = givecard_batch_factory(
        amount=1,
        value=1500,
        campaign=givecard_campaign_factory(),
        supplier=vendor_user_brand.vendor,
        office=vendor_user_brand.office,
        expiration_date=timezone.localdate() - timedelta(days=1),  # Yesterday
    ).generate_givecards()
    # End of setup

    call_command("handle_expired_givecards")

    assert batch.total_balance == 0  # Completely drained
    assert project.product.project_extra.goal_progress_amount == 1000  # Balance transferred to project, goal is 1000
    assert purse.balance == 500  # Excess funds transferred to purse

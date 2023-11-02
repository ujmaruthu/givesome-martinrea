# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from givesome.models import GivesomePromotedProduct


def create_offices_primary_projects(brand_data, charity_data):
    brand_data.office.primary_project = charity_data.project
    brand_data.office2.primary_project = charity_data.project2
    brand_data.office3.primary_project = charity_data.project3
    brand_data.office.save()
    brand_data.office2.save()
    brand_data.office3.save()


def create_offices_promote_projects(brand_data, charity_data):
    GivesomePromotedProduct.objects.create(office=brand_data.office, shop_product=charity_data.project)
    GivesomePromotedProduct.objects.create(office=brand_data.office2, shop_product=charity_data.project2)
    GivesomePromotedProduct.objects.create(office=brand_data.office3, shop_product=charity_data.project3)


def create_layers_of_offices(brand_data):
    """Set office hierarchy. Office > Office2 > Office3"""
    office = brand_data.office
    office2 = brand_data.office2
    office3 = brand_data.office3
    office2.parent = office
    office2.save()
    office3.parent = office2
    office3.save()

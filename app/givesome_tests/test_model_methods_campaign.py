# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

import pytest
from shuup.testing.factories import get_random_filer_image

from givesome_tests.factories import givecard_campaign_factory


@pytest.mark.django_db
def test_campaign_str():
    campaign = givecard_campaign_factory(name="TestCampaign")
    assert str(campaign) == "TestCampaign"


@pytest.mark.django_db
def test_campaign_get_image_thumbnail():
    campaign = givecard_campaign_factory()
    assert campaign.get_image_thumbnail() is None

    campaign.image = get_random_filer_image()
    campaign.save()
    assert campaign.get_image_thumbnail().height == 64

    assert campaign.get_image_thumbnail(size=(0, 0)) is None

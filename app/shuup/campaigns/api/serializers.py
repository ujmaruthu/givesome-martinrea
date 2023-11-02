# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from rest_framework import serializers

from shuup.campaigns.models.context_conditions import HourCondition


class HourConditionSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField()

    class Meta:
        model = HourCondition
        fields = ("id", "hour_start", "hour_end", "days")

    def get_days(self, condition):
        return [v for v in map(int, condition.days.split(","))]


class HourBasketConditionSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField()

    class Meta:
        model = HourCondition
        fields = ("id", "hour_start", "hour_end", "days")

    def get_days(self, condition):
        return [v for v in map(int, condition.days.split(","))]

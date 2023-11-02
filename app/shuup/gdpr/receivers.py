# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.dispatch import receiver

from shuup.front.signals import checkout_complete, company_registration_save, login_allowed, person_registration_save
from shuup.gdpr.utils import create_user_consent_for_all_documents


@receiver(company_registration_save)
def create_consents_company_registration_save(sender, request, user, company, *args, **kwargs):
    create_user_consent_for_all_documents(request.shop, user)


@receiver(person_registration_save)
def create_consents_person_registration_save(sender, request, user, contact, *args, **kwargs):
    create_user_consent_for_all_documents(request.shop, user)


@receiver(login_allowed)
def create_consents_login_allowed(sender, request, user, *args, **kwargs):
    create_user_consent_for_all_documents(request.shop, user)


@receiver(checkout_complete)
def create_consents_checkout_complete(sender, request, user, order, *args, **kwargs):
    if user.is_authenticated:
        create_user_consent_for_all_documents(request.shop, user)

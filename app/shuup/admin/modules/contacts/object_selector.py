# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from typing import Iterable, Tuple

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.core.models import CompanyContact, Contact, PersonContact


def format_contact_name(id, name, email):
    if name and email:
        return f"{name} ({email})"
    if name:
        return name
    if email:
        return email
    return _("Contact {}").format(id)


class ContactAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 3
    model = Contact

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = (
            Contact.objects.filter(
                Q(is_active=True),
                Q(Q(shops=self.shop) | Q(shops__isnull=True)),
                Q(Q(email__icontains=search_term) | Q(name__icontains=search_term)),
            )
            .distinct()
            .values_list("pk", "name", "email")[: self.search_limit]
        )
        return [{"id": id, "name": format_contact_name(id, name, email)} for id, name, email in list(qs)]


class PersonContactAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 4
    model = PersonContact

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = PersonContact.objects.filter(
            Q(is_active=True),
            Q(Q(shops=self.shop) | Q(shops__isnull=True)),
            Q(email__icontains=search_term)
            | Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term),
        )
        qs = qs.distinct().values_list("pk", "name", "email")[: self.search_limit]
        return [{"id": id, "name": format_contact_name(id, name, email)} for id, name, email in list(qs)]


class CompanyContactAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 5
    model = CompanyContact

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = CompanyContact.objects.filter(
            Q(is_active=True),
            Q(Q(shops=self.shop) | Q(shops__isnull=True)),
            Q(name__icontains=search_term) | Q(email__icontains=search_term),
        )
        qs = qs.distinct().values_list("pk", "name", "email")[: self.search_limit]
        return [{"id": id, "name": format_contact_name(id, name, email)} for id, name, email in list(qs)]

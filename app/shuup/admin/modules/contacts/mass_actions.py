# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.admin.modules.contacts.views.list import ContactListView
from shuup.admin.utils.mass_action import BaseExportCSVMassAction
from shuup.admin.utils.picotable import PicotableRedirectMassAction
from shuup.core.models import Contact
from shuup.utils.django_compat import reverse


class EditContactsAction(PicotableRedirectMassAction):
    label = _("Edit Contacts")
    identifier = "mass_action_edit_contact"
    redirect_url = reverse("shuup_admin:contact.mass_edit")


class EditContactGroupsAction(PicotableRedirectMassAction):
    label = _("Set Contact Groups")
    identifier = "mass_action_edit_contact_group"
    redirect_url = reverse("shuup_admin:contact.mass_edit_group")


class ExportContactsCSVAction(BaseExportCSVMassAction):
    identifier = "mass_action_export_contact_csv"
    model = Contact
    view_class = ContactListView
    filename = "contacts.csv"

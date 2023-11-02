# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from .detail import ContactDetailView
from .edit import ContactEditView
from .list import ContactListView
from .mass_edit import ContactGroupMassEditView, ContactMassEditView
from .reset import ContactResetPasswordView

__all__ = [
    "ContactListView",
    "ContactDetailView",
    "ContactResetPasswordView",
    "ContactEditView",
    "ContactGroupMassEditView",
    "ContactMassEditView",
]

# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import Section

from .forms import PrintoutsEmailForm

try:
    import weasyprint
except ImportError:
    weasyprint = None


EMAIL_DEFAULT_BODY = _(
    """Important information regarding your order, see attachment.

Best Regards,
%(shop)s"""
)


class PrintoutsSection(Section):
    identifier = "printouts_section"
    name = _("Printouts")
    icon = "fa-print"
    template = "shuup/order_printouts/admin/section.jinja"
    extra_js = "shuup/order_printouts/admin/section_js.jinja"
    order = 5

    @classmethod
    def visible_for_object(cls, obj, request=None):
        return True

    @classmethod
    def get_context_data(cls, obj, request=None):
        recipient = None
        if obj.customer:
            recipient = obj.customer.email
        elif obj.billing_address:
            recipient = obj.billing_address.email
        data = {
            "to": recipient,
            "subject": _("%(shop)s: Order %(pk)s") % {"shop": obj.shop.name, "pk": obj.pk},
            "body": (EMAIL_DEFAULT_BODY % {"shop": obj.shop.name}).strip(),
        }
        return {"email_form": PrintoutsEmailForm(initial=data), "can_create_pdf": bool(weasyprint)}

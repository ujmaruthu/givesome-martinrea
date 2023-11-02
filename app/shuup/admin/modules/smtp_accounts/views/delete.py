# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView

from shuup.admin.shop_provider import get_shop
from shuup.core.models import SMTPAccount
from shuup.utils.django_compat import reverse


class SMTPAccountDeleteView(DetailView):
    model = SMTPAccount

    def get_queryset(self):
        return SMTPAccount.objects.filter(Q(shop__isnull=True) | Q(shop=get_shop(self.request)))

    def get_success_url(self):
        return reverse("shuup_admin:smtp_account.list")

    def post(self, request, *args, **kwargs):
        smtp_account = self.get_object()
        smtp_account.delete()
        messages.success(request, _(u"Success! %s has been deleted.") % smtp_account)
        return HttpResponseRedirect(self.get_success_url())

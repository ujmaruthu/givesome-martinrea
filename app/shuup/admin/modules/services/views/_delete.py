# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.views.generic import DeleteView

from shuup.core.models import PaymentMethod, ShippingMethod
from shuup.utils.django_compat import reverse_lazy


class PaymentMethodDeleteView(DeleteView):
    model = PaymentMethod
    success_url = reverse_lazy("shuup_admin:payment_method.list")


class ShippingMethodDeleteView(DeleteView):
    model = ShippingMethod
    success_url = reverse_lazy("shuup_admin:shipping_method.list")

# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.views.generic import TemplateView

from shuup.apps.provides import get_provide_objects


class DashboardViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super(DashboardViewMixin, self).get_context_data(**kwargs)
        menu_items = self.get_menu_items()
        context["menu_items"] = menu_items
        selected_item = None
        for item in menu_items:
            if self.request.path.startswith(item.url):
                selected_item = item
        context["selected_item"] = selected_item
        return context

    def get_menu_items(self):
        items = []
        sorted_items = sorted(get_provide_objects("customer_dashboard_items"), key=lambda dashboard: dashboard.ordering)

        for cls in sorted_items:
            c = cls(self.request)
            if c.show_on_menu():
                items.append(c)
        return items

    def dispatch(self, request, *args, **kwargs):
        # these views can only be visible when a contact is available
        if not getattr(request, "person", None):
            from django.http.response import HttpResponseRedirect

            from shuup.utils.django_compat import reverse

            return HttpResponseRedirect(reverse("shuup:index"))
        return super(DashboardViewMixin, self).dispatch(request, *args, **kwargs)


class DashboardView(DashboardViewMixin, TemplateView):
    template_name = "shuup/front/dashboard/dashboard.jinja"

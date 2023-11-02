# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.core.serializers import serialize
from django.db.models import OuterRef, Q, Subquery, Sum
from django.http import Http404, JsonResponse
from django.middleware import csrf
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django_jinja.views.generic import ListView
from shuup.core.models import Order, OrderLineType, PaymentStatus, Product, ShopProductVisibility, get_person_contact
from shuup.utils.i18n import format_money
from shuup.utils.money import Money

from givesome.front.forms.off_platform import OffPlatformDonationForm, VolunteerHoursForm
from givesome.front.utils import filter_valid_projects
from givesome.models import OffPlatformDonation, VolunteerHours


class ProfileView(TemplateView):
    template_name = "shuup/front/profile.jinja"

    def _get_off_platform_totals(self, person_contact, donation_class):
        if donation_class is VolunteerHours:
            aggregate_name = "total_hours"
            kwargs = {aggregate_name: Sum("hours")}
        else:
            aggregate_name = "total_amount"
            kwargs = {aggregate_name: Sum("amount")}

        return donation_class.objects.filter(donor=person_contact).aggregate(**kwargs)[aggregate_name] or 0

    def get_context_data(self, **kwargs):
        user_projects = (
            filter_valid_projects(
                Product.objects.filter(
                    order_lines__type=OrderLineType.PRODUCT,
                    order_lines__order__payment_status=PaymentStatus.FULLY_PAID,
                    order_lines__order__customer=get_person_contact(self.request.user),
                ).distinct(),
                only_always_visible=False,  # Display projects that might have been set to "Listed/Searchable"
                exclude_unapproved=False,  # Migrated products are not approved but should be shown
            )
        )

        projects = (
            user_projects
            .annotate(
                last_donation=Subquery(
                    Order.objects.filter(
                        lines__product=OuterRef("pk"),
                        lines__type=OrderLineType.PRODUCT,
                        payment_status=PaymentStatus.FULLY_PAID,
                        customer=get_person_contact(self.request.user),
                    )
                    .order_by("-order_date")
                    .values("order_date")[:1]
                )
            )
            .order_by("-last_donation")
        )

        donations_db = Order.objects.filter(
            lines__product__in=[project.id for project in user_projects],
            lines__type=OrderLineType.PRODUCT,
            payment_status=PaymentStatus.FULLY_PAID,
            customer=get_person_contact(self.request.user),
        )

        donations = {}
        for donation in donations_db:
            pid = donation.product_ids.first()
            donation_value = donations.get(pid, 0) + donation.taxful_total_price_value
            donations[pid] = round(donation_value, 2)

        context = super(ProfileView, self).get_context_data(**kwargs)
        # On platform stats
        context["lives_impacted"] = (
            projects.aggregate(lives_impacted=Sum("project_extra__lives_impacted"))["lives_impacted"] or 0
        )
        context["total_project_count"] = projects.count()
        context["total_donation_value"] = (round(sum(donations.values()), 2))
        context["donations"] = donations
        # Completed projects include fully funded projects and projects that are not "Always Visible"
        completed_projects = projects.filter(
            Q(project_extra__fully_funded_date__isnull=False)
            | ~Q(shop_products__visibility__in=[ShopProductVisibility.ALWAYS_VISIBLE, ShopProductVisibility.ONLY_VISIBLE_WHEN_PROMOTED])
        )
        context["completed_projects"] = completed_projects
        context["completed_projects_count"] = completed_projects.count()

        ongoing_projects = projects.filter(
            project_extra__fully_funded_date__isnull=True,
            shop_products__visibility__in=[ShopProductVisibility.ALWAYS_VISIBLE, ShopProductVisibility.ONLY_VISIBLE_WHEN_PROMOTED]
        )
        context["ongoing_projects"] = ongoing_projects
        context["ongoing_projects_count"] = ongoing_projects.count()

        # Off platform stats forms
        person_contact = get_person_contact(self.request.user)
        context["total_volunteer_hours"] = f"{self._get_off_platform_totals(person_contact, VolunteerHours)}h"
        context["volunteer_hours_form"] = VolunteerHoursForm()
        context["volunteer_hours_form"].fields["donor"].initial = person_contact

        total_donations = self._get_off_platform_totals(person_contact, OffPlatformDonation)
        total_donations = Money(total_donations, currency=self.request.shop.currency)
        context["total_donations"] = format_money(total_donations).strip("CA")
        context["donations_form"] = OffPlatformDonationForm()
        context["donations_token"] = csrf.get_token(self.request)
        context["donations_form"].fields["donor"].initial = person_contact

        # Apparently jinja can't handle {{ csrf_token }} being used in so many different files for the same page?
        context["token"] = csrf.get_token(self.request)
        return context


def get_model(class_name):
    """Get the correct model for OffPlatform*View to use."""
    if class_name == "VolunteerHours":
        return VolunteerHours
    elif class_name == "OffPlatformDonation":
        return OffPlatformDonation


class OffPlatformMixin(SingleObjectMixin):
    """A mixin to allow off-platform views to be used for both VolunteerHours and OffPlatformDonation"""

    def check_required_attributes(self):
        if self.model is None:
            self.model = get_model(self.kwargs.get("type"))
            self.fields = [field.name for field in self.model._meta.fields[1:]]

    def get_queryset(self):
        self.check_required_attributes()
        return self.model.objects.all()

    def get_object(self, queryset=None):
        class_name = self.kwargs.get("type")
        pk = self.kwargs.get("pk")
        if class_name is None and pk is None:
            raise AttributeError("%s must be called with both an object pk and a type." % self.__class__.__name__)

        instance = self.get_queryset().filter(id=int(pk)).first()
        if instance is None:
            raise Http404()
        return instance


class JsonPostResponseMixin:
    """Serialize the results of POST calls. Child classes must implement standard Django form methods."""

    def get_success_url(self):
        # `success_url` may be expected by child classes, but it's not needed for ajax
        pass

    def form_invalid(self, form):
        super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        super().form_valid(form)
        return JsonResponse(serialize("json", [self.object]), safe=False)


class OffPlatformCreateView(OffPlatformMixin, JsonPostResponseMixin, CreateView):
    pass


class OffPlatformUpdateView(OffPlatformMixin, JsonPostResponseMixin, UpdateView):
    pass


class OffPlatformListView(ListView):
    """A generic list view for both VolunteerHours and OffPlatformDonations. Note: ListView should not inherit from
    a child of SingleObjectMixin.
    """

    def get_ordering(self):
        for field in self.model._meta.get_fields():
            if field.__class__.__name__ == "DateField":
                return "-" + field.name

    def get_queryset(self):
        self.model = get_model(self.kwargs.get("type"))
        return self.model.objects.filter(donor=get_person_contact(self.request.user)).order_by(self.get_ordering())

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return JsonResponse(serialize("json", self.get_queryset()), safe=False)


class OffPlatformDeleteView(OffPlatformMixin, JsonPostResponseMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        deleted_data = serialize("json", [self.object])
        self.object.delete()
        return JsonResponse(deleted_data, safe=False)

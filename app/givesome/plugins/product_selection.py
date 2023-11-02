# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import json

from django import forms
from django.db.models import Subquery
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum, EnumField
from shuup.admin.forms.widgets import ProductChoiceWidget
from shuup.core.models import Product, ProductMode
from shuup.xtheme.plugins.forms import TranslatableField
from shuup.xtheme.plugins.products import ProductSelectionConfigForm, ProductSelectionPlugin

from givesome.front.utils import filter_valid_projects
from givesome.models import CompletionVideo


class ProductActionCategory(Enum):
    RANDOM = "?"
    NAME = "translations__name"
    ID = "id"
    LIVES_IMPACTED = "project_extra__lives_impacted"
    PERCENTAGE_TO_FINISH = "to_finish"

    class Labels:
        RANDOM = _("Random")
        NAME = _("Name")
        ID = _("Id")
        LIVES_IMPACTED = _("Lives impacted")
        PERCENTAGE_TO_FINISH = _("Percentage until completed")


class GivesomeProductSelectionPlugin(ProductSelectionPlugin):
    identifier = "givesome_product_selection"
    name = _("Givesome Product Selection")
    fields = [
        ("title", TranslatableField(label=_("Title"), required=False, initial="")),
        (
            "order_by",
            EnumField(ProductActionCategory).formfield(
                form_class=forms.ChoiceField,
                label=_("Order by"),
                initial=ProductActionCategory.RANDOM,
                help_text=_("Filter report results by a date range."),
            ),
        ),
        (
            "ascending",
            forms.BooleanField(
                label=_("Use ascending order"),
                help_text=_(
                    "If check products will be sorted in a ascending order, else it will be a descending. "
                    "Note: this doesn't work for a random order"
                ),
                initial=False,
                required=False,
            ),
        ),
    ]

    def get_cache_key(self, context, **kwargs) -> str:
        title = self.get_translated_value("title")
        products = self.config.get("products")
        order_by = self.config.get("order_by", ProductActionCategory.RANDOM)
        ascending = self.config.get("ascending")
        return str((get_language(), title, products, order_by, ascending))

    def get_context_data(self, context):
        context = super().get_context_data(context)
        products = context["products"]
        order_by = self.config.get("order_by", ProductActionCategory.RANDOM)
        ascending = self.config.get("ascending")

        if order_by == ProductActionCategory.RANDOM:
            products = products.order_by("?")
        else:

            if order_by == ProductActionCategory.PERCENTAGE_TO_FINISH:
                products = sorted(
                    products, key=(lambda x: x.project_extra.goal_progress_percentage), reverse=(not ascending)
                )
            else:
                ordering = order_by.value
                if not ascending:
                    ordering = "-%s" % ordering
                products = products.order_by(ordering).distinct()

        context["products"] = products
        return context


class GivesomeModelChoiceField(forms.ModelChoiceField):
    def to_python(self, value):
        if value:
            return int(value)


class GivesomeProductChoiceWidget(ProductChoiceWidget):
    filter = json.dumps(
        {
            "modes": [ProductMode.NORMAL.value],
            "givesome_valid_project": True,
        }
    )


class GivesomeProductSelectionConfigForm(ProductSelectionConfigForm):
    product_widget = GivesomeProductChoiceWidget

    def populate(self):
        super().populate()
        self.fields.pop("products")
        number_of_products = self.plugin.config.get("number_of_products", 1)

        for i in range(1, number_of_products + 1):
            name = "product%s" % (str(i),)
            self.fields[name] = GivesomeModelChoiceField(
                label=_("Project %s") % (str(i),),
                queryset=Product.objects.all(),
                widget=self.product_widget(clearable=True),
                required=False,
                initial=self.plugin.config.get(name, None),
            )


class GivesomeProductSelectionWithOrderPlugin(ProductSelectionPlugin):
    identifier = "givesome_product_selection_order_specific"
    name = _("Givesome Project Selection with specific order")
    editor_form_class = GivesomeProductSelectionConfigForm
    fields = [
        ("title", TranslatableField(label=_("Title"), required=False, initial="")),
        ("number_of_products", forms.IntegerField(label=_("Number of projects to show"), required=True, initial=1)),
    ]

    def get_cache_key(self, context, **kwargs) -> str:
        title = self.get_translated_value("title")
        user = context.parent.get("user")
        currency = (
            "CAD"
            if user is None or not hasattr(user, "preferred_currency") or not user.preferred_currency.currency
            else user.preferred_currency.currency.identifier
        )
        number_of_products = self.config.get("number_of_products", 0)
        products = [self.config.get("product%s" % (str(i),)) for i in range(1, number_of_products + 1)]
        return str((get_language(), title, number_of_products, *products, currency))

    def _get_ordered_product_ids(self):
        number_of_products = self.config.get("number_of_products", 0)
        products_ordering_id = dict(
            [
                (self.config.get("product%s" % (str(i),)), i)
                for i in range(1, number_of_products + 1)
                if self.config.get("product%s" % (str(i),))
            ]
        )
        return products_ordering_id

    def get_context_data(self, context):
        context = super().get_context_data(context)
        products_ordering_id = self._get_ordered_product_ids()

        products_qs = filter_valid_projects(Product.objects.filter(id__in=products_ordering_id.keys()))

        products = list(products_qs)
        products = sorted(products, key=(lambda x: products_ordering_id[x.id]))

        context["products"] = products
        return context


class GivesomeVideoProductChoiceWidget(ProductChoiceWidget):
    filter = json.dumps(
        {
            "modes": [ProductMode.NORMAL.value],
            "givesome_valid_project": True,
            "has_video": True,
            "recently_funded_first": True,
        }
    )


class GivesomeVideoSelectionConfigForm(GivesomeProductSelectionConfigForm):
    product_widget = GivesomeVideoProductChoiceWidget


class GivesomeVideoSelectionWithOrderPlugin(GivesomeProductSelectionWithOrderPlugin):
    identifier = "givesome_video_selection_order_specific"
    name = _("Givesome Video Selection with specific order")
    template_name = "givesome/plugins/video_selection.jinja"
    editor_form_class = GivesomeVideoSelectionConfigForm
    fields = [
        ("title", TranslatableField(label=_("Title"), required=False, initial="")),
        ("number_of_products", forms.IntegerField(label=_("Number of videos to show"), required=True, initial=1)),
    ]

    def get_context_data(self, context):
        context = super(ProductSelectionPlugin, self).get_context_data(context)
        products_ordering_id = self._get_ordered_product_ids()

        videos = (
            CompletionVideo.objects.filter(
                pk__in=Subquery(
                    CompletionVideo.objects.filter(project__id__in=products_ordering_id.keys())
                    .distinct("linked_on", "project_id")
                    .order_by("-linked_on")
                    .values("pk")
                )
            )
            .prefetch_related("project")
            .order_by("-linked_on")
        )
        videos = sorted(list(videos), key=(lambda video: products_ordering_id[video.project.id]))

        context["featured_videos"] = videos
        return context

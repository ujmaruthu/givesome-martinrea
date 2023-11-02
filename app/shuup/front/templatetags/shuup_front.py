# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import django_jinja
from django.utils.functional import SimpleLazyObject
from django.utils.safestring import mark_safe
from django_jinja import library
from functools import lru_cache
from markdown import Markdown

from shuup import configuration
from shuup.apps.provides import get_provide_objects
from shuup.core.setting_keys import SHUUP_LENGTH_UNIT, SHUUP_MASS_UNIT
from shuup.utils.django_compat import force_text


class HelpersNamespace(object):
    pass


def _get_helpers():
    helpers = HelpersNamespace()
    from shuup.front.template_helpers import basket, category, general, order, product, urls

    helpers.general = general
    helpers.basket = basket
    helpers.order = order
    helpers.product = product
    helpers.category = category
    helpers.urls = urls
    for namespace in get_provide_objects("front_template_helper_namespace"):
        if namespace and getattr(namespace, "name", None):
            if callable(namespace):  # If it's a class, instantiate it
                namespace = namespace()
            setattr(helpers, namespace.name, namespace)
    return helpers


library.global_function(name="shuup", fn=SimpleLazyObject(_get_helpers))


@lru_cache()
def _cached_markdown(str_value):

    return Markdown(
        extensions=[
            "markdown.extensions.extra",
            "markdown.extensions.nl2br",
        ],
        output_format="html5",
    ).convert(str_value)


@library.filter(name="markdown")
def markdown(value):
    return mark_safe(_cached_markdown(force_text(value)))


@library.filter(name="replace_field_attrs")
def replace_field_attrs(field, **attrs):
    for attr, value in attrs.items():
        setattr(field.field, attr, value)
    return field


@django_jinja.library.global_function
def get_mass_and_length_units():
    """
    Returns the mass and the length unit from settings

    :rtype: Tuple[str, str]
    """
    return configuration.get(None, SHUUP_MASS_UNIT), configuration.get(None, SHUUP_LENGTH_UNIT)

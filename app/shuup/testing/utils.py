# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import contextlib
import django.conf
import inspect
import sys
import types
import uuid
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.test import override_settings
from django.urls import clear_url_caches, get_urlconf, set_urlconf
from django.utils.module_loading import import_string
from django.utils.translation import activate, get_language

from shuup import configuration
from shuup.admin import shop_provider
from shuup.configuration import get as original_configuration_get
from shuup.core.setting_keys import SHUUP_ENABLE_MULTIPLE_SHOPS
from shuup.front.setting_keys import (
    SHUUP_ALLOW_COMPANY_REGISTRATION,
    SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD,
    SHUUP_REGISTRATION_REQUIRES_ACTIVATION,
)
from shuup.utils.django_compat import RegexPattern, URLResolver, get_middleware_classes


def apply_request_middleware(request, **attrs):
    """
    Apply all the `process_request` capable middleware configured
    into the given request.

    :param request: The request to massage.
    :type request: django.http.HttpRequest
    :param attrs: Additional attributes to set after massage.
    :type attrs: dict
    :return: The same request, massaged in-place.
    :rtype: django.http.HttpRequest
    """
    for middleware_path in get_middleware_classes():
        mw_class = import_string(middleware_path)
        current_language = get_language()

        try:
            mw_instance = mw_class()
        except MiddlewareNotUsed:
            continue

        for key, value in attrs.items():
            setattr(request, key, value)

        if hasattr(mw_instance, "process_request"):
            mw_instance.process_request(request)

        activate(current_language)

    assert request.shop

    if not attrs.get("skip_session", False):
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        if mod.__name__.startswith("shuup_tests.admin"):
            shop_provider.set_shop(request, request.shop)

    return request


def apply_view_middleware(request):
    """
    Apply all the `process_view` capable middleware configured
    into the given request.

    The logic is roughly copied from
    django.core.handlers.base.BaseHandler.get_response

    :param request: The request to massage.
    :type request: django.http.HttpRequest
    :return: The same request, massaged in-place.
    :rtype: django.http.HttpRequest
    """
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    set_urlconf(urlconf)

    resolver = URLResolver(RegexPattern(r"^/"), urlconf)
    resolver_match = resolver.resolve(request.path_info)
    callback, callback_args, callback_kwargs = resolver_match
    request.resolver_match = resolver_match

    for middleware_path in get_middleware_classes():
        mw_class = import_string(middleware_path)
        try:
            mw_instance = mw_class()
        except MiddlewareNotUsed:
            continue

        if hasattr(mw_instance, "process_view"):
            mw_instance.process_view(request, callback, callback_args, callback_kwargs)

    return request


def apply_all_middleware(request, **attrs):
    """
    Apply all the `process_request` and `process_view` capable
    middleware configured into the given request.

    :param request: The request to massage.
    :type request: django.http.HttpRequest
    :param attrs: Additional attributes to set to the request after massage.
    :type attrs: dict
    :return: The same request, massaged in-place.
    :rtype: django.http.HttpRequest
    """
    request = apply_view_middleware(apply_request_middleware(request))
    for key, value in attrs.items():
        setattr(request, key, value)
    return request


@contextlib.contextmanager
def replace_urls(patterns, extra=None):
    """
    Context manager to replace the root URLconf with a list of URLpatterns in-memory.

    This is admittedly somewhat black-magicky.

    :param patterns: List of URLpatterns
    :type patterns: list[RegexURLResolver]
    :param extra: Dict to add to the created urlconf
    :type extra: dict
    """
    old_urlconf = get_urlconf(default=django.conf.settings.ROOT_URLCONF)
    urlconf_module_name = "replace_urls_%s" % uuid.uuid4()
    module = types.ModuleType(urlconf_module_name)
    module.urlpatterns = patterns
    module.__dict__.update(extra or ())
    sys.modules[urlconf_module_name] = module
    set_urlconf(urlconf_module_name)
    clear_url_caches()
    with override_settings(ROOT_URLCONF=urlconf_module_name):
        yield
    set_urlconf(old_urlconf)
    clear_url_caches()
    sys.modules.pop(urlconf_module_name)


def get_multiple_shops_false_configuration(shop, key, default=None):
    if key == SHUUP_ENABLE_MULTIPLE_SHOPS:
        return False
    return original_configuration_get(shop, key, default)


def get_multiple_shops_true_configuration(shop, key, default=None):
    if key == SHUUP_ENABLE_MULTIPLE_SHOPS:
        return True
    return original_configuration_get(shop, key, default)


def get_registration_requires_activation_true(shop, key, default=None):
    if key == SHUUP_REGISTRATION_REQUIRES_ACTIVATION:
        return True
    return original_configuration_get(shop, key, default)


def get_registration_requires_activation_false(shop, key, default=None):
    if key == SHUUP_REGISTRATION_REQUIRES_ACTIVATION:
        return False
    return original_configuration_get(shop, key, default)


def get_customer_information_allow_picture_upload_true(shop, key, default=None):
    if key == SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD:
        return True
    return original_configuration_get(shop, key, default)


def get_customer_information_allow_picture_upload_false(shop, key, default=None):
    if key == SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD:
        return False
    return original_configuration_get(shop, key, default)


def get_allow_company_registration_false(shop, key, default=None):
    if key == SHUUP_ALLOW_COMPANY_REGISTRATION:
        return False
    return original_configuration_get(shop, key, default)


def get_allow_company_registration_true(shop, key, default=None):
    if key == SHUUP_ALLOW_COMPANY_REGISTRATION:
        return True
    return original_configuration_get(shop, key, default)


class override_configuration:
    def __init__(self, shop=None, encryted=False, **overrides):
        self.shop = shop
        self.encrypted = encryted
        self.overrides = overrides
        self._original_state = {}

    def __enter__(self, *args, **kwargs):
        for key, value in self.overrides.items():
            self._original_state[key] = configuration.get(self.shop, key)
            configuration.set(self.shop, key, value, encrypted=self.encrypted)

    def __exit__(self, *args, **kwargs):
        for key, value in self._original_state.items():
            configuration.set(self.shop, key, value, encrypted=self.encrypted)

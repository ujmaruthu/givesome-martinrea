# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
import hashlib
import os
import requests
import six
from django.conf import settings
from django.core.cache.backends.base import InvalidCacheKey
from django_jinja import library
from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.templatetags.thumbnail import RE_SIZE

from shuup.core import cache
from shuup.core.models import ProductMediaKind
from shuup.front.utils.product import get_embed_vimeo, get_embed_youtube

VIMEO_API = "https://vimeo.com/api/oembed.json?url={}"


def process_thumbnailer_options(kwargs):
    default_options = getattr(settings, "THUMBNAIL_DEFAULT_OPTIONS", {})
    options = {}
    options.update(default_options)
    options.update(kwargs)
    size = options.setdefault("size", (128, 128))
    if isinstance(size, six.text_type):
        m = RE_SIZE.match(size)
        if m:
            options["size"] = (int(m.group(1)), int(m.group(2)))
        else:
            raise ValueError("Error! %r is not a valid size." % size)
    return options


def _get_video_thumbnail(video_url, **kwargs):
    if "youtube.com" in video_url:
        return "https://img.youtube.com/vi/{}/0.jpg".format(get_embed_youtube(video_url).split("/")[-1])
    elif "vimeo.com" in video_url:
        try:
            params = {"responsive": True}
            if kwargs.get("size"):
                size = kwargs.get("size")
                params["width"] = size[0]
                params["height"] = size[1]
            vimeo_details = requests.get(VIMEO_API.format(video_url), params=params)
            return vimeo_details.json().get("thumbnail_url_with_play_button")
        except ValueError:
            return None
    return None


def _get_cached_thumbnail_url(source, **kwargs):
    from filer.models.filemodels import File

    from shuup.core.models import ProductMedia

    sorted_items = dict(sorted(kwargs.items(), key=lambda item: item[0]))
    kwargs_hash = hashlib.sha1(str(sorted_items).encode("utf-8")).hexdigest()
    cache_key = None

    if isinstance(source, (File, ProductMedia)) and source.pk:
        cache_key = "thumbnail_{}_{}:_cached_thumbnail_{}".format(source.pk, source.__class__.__name__, kwargs_hash)

    elif isinstance(source, six.string_types):
        cache_key = "_cached_thumbnail_url_{}".format(kwargs_hash)

    elif hasattr(source, "url") and source.url:
        cache_key = "_cached_thumbnail_url_{}".format(source.url)

    if cache_key:
        return cache_key, cache.get(cache_key)
    return (None, None)


def _get_cached_video_url(source, **kwargs):
    sorted_items = dict(sorted(kwargs.items(), key=lambda item: item[0]))
    kwargs_hash = hashlib.sha1(str(sorted_items).encode("utf-8")).hexdigest()
    cache_key = "_cached_product_video_url_{}_{}".format(source.pk, kwargs_hash)
    if cache_key:
        try:
            return cache_key, cache.get(cache_key)
        except InvalidCacheKey:
            pass
    return (None, None)


@library.filter
def embed(source, **kwargs):
    if not source:
        return None
    cache_key, cached_video_url = _get_cached_video_url(source, **kwargs)
    if cached_video_url is not None:
        return cached_video_url
    if source.kind == ProductMediaKind.VIDEO and source.external_url:
        if "youtube.com" in source.external_url:
            cached_video_url = get_embed_youtube(source.external_url)
        elif "vimeo.com" in source.external_url:
            cached_video_url = get_embed_vimeo(source.external_url)
        else:
            cached_video_url = source.external_url
        if cache_key and cached_video_url:
            cache.set(cache_key, cached_video_url)
        return cached_video_url
    return source.external_url or source.url


def video_thumbnail(source, alias=None, generate=True, **kwargs):
    cache_key, cached_thumbnail_url = _get_cached_thumbnail_url(source, alias=alias, generate=generate, **kwargs)

    if cached_thumbnail_url is not None:
        return cached_thumbnail_url
    cached_thumbnail_url = _get_video_thumbnail(source.external_url, **kwargs)
    if cache_key:
        cache.set(cache_key, cached_thumbnail_url)
    return cached_thumbnail_url


@library.filter
def thumbnail(source, alias=None, generate=True, **kwargs):
    if not source:
        return None
    if hasattr(source, "kind") and source.kind == ProductMediaKind.VIDEO and source.external_url:
        return video_thumbnail(source, alias=alias, generate=generate, **kwargs)

    cache_key, cached_thumbnail_url = _get_cached_thumbnail_url(source, alias=alias, generate=generate, **kwargs)

    if cached_thumbnail_url is not None:
        return cached_thumbnail_url

    thumbnailer_instance = get_thumbnailer(source)

    if not thumbnailer_instance:
        return None

    if _is_svg(thumbnailer_instance):
        return source.url if hasattr(source, "url") else None

    if alias:
        options = aliases.get(alias, target=thumbnailer_instance.alias_target)
        options.update(process_thumbnailer_options(kwargs))
    else:
        options = process_thumbnailer_options(kwargs)

    try:
        thumbnail_instance = thumbnailer_instance.get_thumbnail(options, generate=generate)
        thumbnail_url = thumbnail_instance.url
        if cache_key:
            cache.set(cache_key, thumbnail_url)
        return thumbnail_url
    except (IOError, InvalidImageFormatError, ValueError):
        return None


def _is_svg(thumbnailer_instance):
    file_name = getattr(thumbnailer_instance, "name", None)
    if not file_name:
        return False
    return bool(os.path.splitext(file_name)[1].lower() == ".svg")


@library.filter
def thumbnailer(source):
    return get_thumbnailer(source)

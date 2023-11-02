# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import BaseModelFormSet
from django.utils.translation import activate, get_language
from shuup.admin.form_part import TemplatedFormDef
from shuup.admin.forms import ShuupAdminForm
from shuup_multivendor.admin_module.form_parts.product import VendorProductBaseFormPart

from givesome.models import CompletionVideo


class CompletionVideoURLForm(ShuupAdminForm):
    class Meta:
        model = CompletionVideo
        fields = ["url", "description"]

    def clean_url(self):
        """
        Store the embed version of the video url, which the user might not know to supply. Assume properly
        formatted urls are valid.
        """
        url = self.cleaned_data["url"]
        watch = "https://www.youtube.com/watch?v="
        embed = "https://www.youtube.com/embed/"
        if not url.startswith(watch) and not url.startswith(embed):
            raise ValidationError("Please supply a valid YouTube link. E.g. https://www.youtube.com/watch?v=12345abcde")
        if url.startswith(watch):
            video_id = url.split("=")[1].split("?")[0]
            url = "{}{}".format(embed, video_id)
        # Note: custom kwargs for formsets created by `formset_factory` are not supported, so the origin
        # scheme/domain will need to be set elsewhere.
        if "?origin=" not in url:
            url = "{}?origin=".format(url)
        return url

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product")
        self.base_fields["description"].widget.attrs.update({"rows": 3})
        super().__init__(*args, **kwargs)


class CompletionVideoURLFormSet(BaseModelFormSet):
    model = CompletionVideo
    form_class = CompletionVideoURLForm
    can_delete = True
    validate_min = False
    min_num = 0
    validate_max = False
    max_num = 10
    absolute_max = 10
    can_order = False
    extra = 0

    def __init__(self, **kwargs):
        self.product = kwargs.pop("product", None)
        self.languages = kwargs.pop("languages", None)
        super().__init__(**kwargs)

    def form(self, **kwargs):
        kwargs.setdefault("product", self.product)
        kwargs.setdefault("languages", settings.LANGUAGES)
        kwargs.setdefault("default_language", settings.PARLER_DEFAULT_LANGUAGE_CODE)
        return self.form_class(**kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(project=self.product)


class CompletionVideoURLFormPart(VendorProductBaseFormPart):
    name = "url"

    def get_initial(self):
        initial = []
        for video in CompletionVideo.objects.filter(project=self.object.product):
            description = video.safe_translation_getter("description") or ""
            initial.append({"pk": video.pk, "url": video.url, f"description__{get_language()}": description})
        return initial

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            CompletionVideoURLFormSet,
            template_name="givesome/admin/projects/completion_video.jinja",
            required=False,
            kwargs={
                "initial": self.get_initial(),
                "languages": settings.LANGUAGES,
                "product": self.object.product,
            },
        )

    def save(self, data):
        for link in data:
            # Ignore videos where url is empty
            if "url" not in link or link["url"] == "":
                continue

            # Delete removed videos
            if link["DELETE"]:
                CompletionVideo.objects.filter(project=self.object.product, url=link["url"]).delete()
                continue

            # Add origin to url
            # TODO move this to a model method
            if "origin" not in link["url"]:
                url = "{}{}&origin=://{}".format(link["url"], self.request.scheme, self.request.get_host())
            elif link["url"].endswith("origin="):
                url = "{}{}://{}".format(link["url"], self.request.scheme, self.request.get_host())
            else:
                url = link["url"]

            instance, __ = CompletionVideo.objects.update_or_create(
                project=self.object.product,
                url=url,
                defaults=dict(url=url),
            )

            for lang, __ in settings.LANGUAGES:
                activate(lang)
                video = CompletionVideo.objects.get(pk=instance.pk)
                video.description = link[f"description__{lang}"]
                video.save()
            activate(settings.PARLER_DEFAULT_LANGUAGE_CODE)

    def form_valid(self, form_group):
        if self.name in form_group.cleaned_data:
            # Check that there is data to save.
            data = form_group.cleaned_data[self.name]
            if len(data) > 0 and data[0]:
                self.save(form_group.cleaned_data[self.name])
        return super().form_valid(form_group)

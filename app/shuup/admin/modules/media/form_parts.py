# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the Shuup Commerce Inc -
# SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
# and the Licensee.

from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.modules.media.forms import MediaFolderForm


class MediaFolderBaseFormPart(FormPart):
    priority = 1

    def get_form_defs(self):
        yield TemplatedFormDef(
            "media_form",
            MediaFolderForm,
            template_name="shuup/admin/media/edit_folder.jinja",
            required=False,
            kwargs={
                "instance": self.object,
            },
        )

    def form_valid(self, form):
        self.object = form["media_form"].save()

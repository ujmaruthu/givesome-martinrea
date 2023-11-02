# -*- coding: utf-8 -*-
# Addition by givesome management
from django.utils.translation import ugettext_lazy as _
from shuup.admin.base import Section
from shuup.admin.form_part import FormPart, TemplatedFormDef

from givesome.admin_module.forms.givesome_competition import GivesomeCompetitionForm
from givesome.models import GivesomeCompetition


class GivesomeCompetitionBaseFormPart(FormPart):
    priority = -1000

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            GivesomeCompetitionForm,
            template_name="givesome/admin/givesome_competition/_edit_base.jinja",
            required=True,
            kwargs={"instance": self.object, "request": self.request},
        )

    def form_valid(self, form_group):
        self.object = form_group["base"].save()
        return self.object

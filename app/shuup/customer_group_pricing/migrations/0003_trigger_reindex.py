# -*- coding: utf-8 -*-
from django.db import migrations

from shuup import configuration


def reindex_product_catalog(apps, schema_editor):
    configuration.set(None, "product_catalog_needs_reindex", True)


class Migration(migrations.Migration):
    dependencies = [
        ("shuup_customer_group_pricing", "0002_discounts"),
    ]
    operations = [migrations.RunPython(reindex_product_catalog, migrations.RunPython.noop)]
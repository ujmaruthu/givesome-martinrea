# Generated by Django 2.2.21 on 2021-07-19 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0054_add_supplier_to_purse'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorextra',
            name='allow_purse',
            field=models.BooleanField(default=False),
        ),
    ]

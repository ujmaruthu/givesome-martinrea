# Generated by Django 2.2.24 on 2021-09-23 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0062_vendorextra_enable_receipting'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectextra',
            name='enable_receipting',
            field=models.BooleanField(default=False),
        ),
    ]

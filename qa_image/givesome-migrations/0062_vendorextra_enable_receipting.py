# Generated by Django 2.2.24 on 2021-09-23 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0061_purchasereportdata_receipt'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorextra',
            name='enable_receipting',
            field=models.BooleanField(default=False),
        ),
    ]

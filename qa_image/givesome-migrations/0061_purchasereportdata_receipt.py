# Generated by Django 2.2.24 on 2021-09-06 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0060_receiptingmessages_receiptingmessagestranslation'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasereportdata',
            name='receipt',
            field=models.BooleanField(default=False, verbose_name='Donor wants receipt'),
        ),
    ]

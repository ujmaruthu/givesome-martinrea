# Generated by Django 2.2.24 on 2022-09-08 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0072_vendorextra_sponsor_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectextra',
            name='show_promoted',
            field=models.BooleanField(default=True, help_text='Show project as promoted', verbose_name='Show in promoted'),
        ),
    ]

# Generated by Django 2.2.17 on 2021-04-07 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0040_add_sponsored_by_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectextra',
            name='featured',
            field=models.BooleanField(default=False, help_text="Feature this project's video on the home page."),
        ),
    ]

# Generated by Django 2.2.24 on 2022-09-19 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0073_projectextra_show_promoted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectextra',
            name='show_promoted',
        ),
        migrations.AddField(
            model_name='vendorextra',
            name='show_promoted',
            field=models.BooleanField(default=True, help_text='Show promoted projects', verbose_name='Show promoted projects'),
        ),
    ]
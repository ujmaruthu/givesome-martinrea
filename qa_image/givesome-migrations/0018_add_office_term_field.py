# Generated by Django 2.2.17 on 2020-12-10 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0017_office_promoted_projects'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorextra',
            name='office_term',
            field=models.CharField(blank=True, default='Office', help_text='Enter a term you want to use for your offices/chapters/locations.', max_length=32, null=True, verbose_name='Office term'),
        ),
    ]

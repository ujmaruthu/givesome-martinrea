# Generated by Django 2.2.16 on 2020-11-10 20:12

from django.db import migrations
import shuup.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sustainabilitygoal',
            name='identifier',
            field=shuup.core.fields.InternalIdentifierField(blank=True, editable=False, max_length=64, null=True, unique=False),
        ),
    ]

# Generated by Django 2.2.17 on 2021-01-07 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0020_givecard_batch_generated_on_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectextra',
            name='lives_impacted',
            field=models.IntegerField(default=0, help_text='The total number of projected lives to be impacted.'),
        ),
    ]

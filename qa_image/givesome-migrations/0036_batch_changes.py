# Generated by Django 2.2.17 on 2021-03-08 16:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0035_nullifiedgivecardbatch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='givecardbatch',
            name='amount',
            field=models.PositiveIntegerField(default=1, help_text='Amount of Givecards to generate in this batch.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100000)], verbose_name='quantity'),
        ),
        migrations.AlterField(
            model_name='givecardbatch',
            name='value',
            field=models.PositiveIntegerField(default=2, help_text='Value ($) on all the Givecards generated in this batch.', validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(100000)], verbose_name='value'),
        ),
        migrations.AlterField(
            model_name='givecardcampaigntranslation',
            name='message',
            field=models.TextField(blank=True, help_text='Add a message to be shown to donors when they redeem a Givecard belonging to this campaign.', max_length=500, null=True, verbose_name='Message'),
        ),
    ]

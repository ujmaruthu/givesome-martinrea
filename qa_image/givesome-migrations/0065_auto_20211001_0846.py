# Generated by Django 2.2.24 on 2021-10-01 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0064_auto_20210927_0829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='charity_page',
            field=models.TextField(default='', help_text='Seen when hovering over the charity page receipting symbol.'),
        ),
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='checkout_givecard',
            field=models.TextField(default='', help_text='Seen when donating by Givecard.'),
        ),
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='checkout_no',
            field=models.TextField(default='', help_text='When donors do not wish to receive a receipt.'),
        ),
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='checkout_warn',
            field=models.TextField(default='', help_text='When donors wish to receive a receipt, but have incomplete info.'),
        ),
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='checkout_yes',
            field=models.TextField(default='', help_text='When donors wish to receive a receipt.'),
        ),
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='portfolio',
            field=models.TextField(default='', help_text='Seen by donors who are editing their profiles.'),
        ),
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='project_card',
            field=models.TextField(default='', help_text='Seen when hovering over the project card receipting symbol.'),
        ),
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='project_page',
            field=models.TextField(default='', help_text='Seen when hovering over the project page receipting symbol.'),
        ),
        migrations.AlterField(
            model_name='receiptingmessagestranslation',
            name='welcome',
            field=models.TextField(default='', help_text='Seen by users when they enter the site.'),
        ),
    ]

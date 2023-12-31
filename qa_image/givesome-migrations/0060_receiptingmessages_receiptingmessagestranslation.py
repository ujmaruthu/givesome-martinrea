# Generated by Django 2.2.24 on 2021-08-06 15:27

from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0059_add_registration_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiptingMessages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ReceiptingMessagesTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('welcome', models.CharField(default='', help_text='Seen by users when they enter the site.', max_length=255)),
                ('project_card', models.CharField(default='', help_text='Seen when hovering over the project card receipting symbol.', max_length=255)),
                ('charity_page', models.CharField(default='', help_text='Seen when hovering over the charity page receipting symbol.', max_length=255)),
                ('project_page', models.CharField(default='', help_text='Seen when hovering over the project page receipting symbol.', max_length=255)),
                ('checkout_no', models.CharField(default='', help_text='When donors do not wish to receive a receipt.', max_length=255)),
                ('checkout_yes', models.CharField(default='', help_text='When donors wish to receive a receipt.', max_length=255)),
                ('checkout_warn', models.CharField(default='', help_text='When donors wish to receive a receipt, but have incomplete info.', max_length=255)),
                ('checkout_givecard', models.CharField(default='', help_text='Seen when donating by Givecard.', max_length=255)),
                ('portfolio', models.CharField(default='', help_text='Seen by donors who are editing their profiles.', max_length=255)),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='givesome.ReceiptingMessages')),
            ],
            options={
                'verbose_name': 'receipting messages Translation',
                'db_table': 'givesome_receiptingmessages_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]

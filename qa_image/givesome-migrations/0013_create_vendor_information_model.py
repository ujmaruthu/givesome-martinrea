# Generated by Django 2.2.16 on 2020-12-03 13:56

from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models
import shuup.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0012_create_project_extra_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', shuup.core.fields.InternalIdentifierField(blank=True, editable=False, max_length=64, null=True, unique=False)),
            ],
            options={
                'verbose_name_plural': 'Vendor Information',
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.AlterField(
            model_name='sustainabilitygoallogentry',
            name='identifier',
            field=models.CharField(blank=True, db_index=True, max_length=256, verbose_name='identifier'),
        ),
        migrations.AlterField(
            model_name='sustainabilitygoallogentry',
            name='message',
            field=models.CharField(max_length=1024, verbose_name='message'),
        ),
        migrations.AlterField(
            model_name='vendorextra',
            name='color',
            field=models.CharField(blank=True, help_text="Enter the hex code of the organization's main colour.", max_length=7, null=True, verbose_name='Hex colour code'),
        ),
        migrations.CreateModel(
            name='VendorInformationTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=64)),
                ('page', models.TextField(help_text='Describe any information that vendors and charities should know.', verbose_name='Vendor and Charity Information')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='givesome.VendorInformation')),
            ],
            options={
                'verbose_name': 'vendor information Translation',
                'db_table': 'givesome_vendorinformation_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
# Generated by Django 2.2.24 on 2021-09-16 20:40

import django.db.models.deletion
import enumfields.fields
import shuup_mirage_field.fields
from django.db import migrations, models

import shuup.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0102_improve_api_documentation'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMTPAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Account name')),
                ('host', models.CharField(max_length=255, verbose_name='Host')),
                ('port', models.IntegerField(default=587, verbose_name='Port')),
                ('default_from_email', models.CharField(help_text='The default sender\'s email, e.g. support@store.com or even "Store Support" <support@store.com>', max_length=250, verbose_name='Default from email')),
                ('username', shuup_mirage_field.fields.EncryptedCharField(max_length=255, verbose_name='Username')),
                ('password', shuup_mirage_field.fields.EncryptedCharField(max_length=255, verbose_name='Password')),
                ('protocol', enumfields.fields.EnumField(default='none', enum=shuup.core.models.SMTPProtocol, max_length=10, verbose_name='Connection protocol')),
                ('timeout', models.IntegerField(default=10, help_text='Specifies a timeout in seconds for blocking operations like the connection attempt.', verbose_name='Timeout')),
                ('ssl_certfile', shuup_mirage_field.fields.EncryptedTextField(blank=True, help_text='PEM-formatted certificate chain to use for the SSL connection', null=True, verbose_name='SSL certificate file')),
                ('ssl_keyfile', shuup_mirage_field.fields.EncryptedTextField(blank=True, help_text='PEM-formatted private key to use for the SSL connection', null=True, verbose_name='SSL key file')),
                ('default_account', models.BooleanField(default=False)),
                ('shop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='smtp_accounts', to='shuup.Shop')),
            ],
        ),
        migrations.AddConstraint(
            model_name='smtpaccount',
            constraint=models.UniqueConstraint(condition=models.Q(('default_account', True), ('shop__isnull', False)), fields=('shop',), name='unique_default_accounts'),
        ),
        migrations.AddConstraint(
            model_name='smtpaccount',
            constraint=models.UniqueConstraint(condition=models.Q(('default_account', True), ('shop', None)), fields=('default_account',), name='unique_global_default_account'),
        ),
    ]

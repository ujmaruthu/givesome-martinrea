# Generated by Django 2.2.24 on 2021-11-08 17:52

from django.db import migrations, models
import django.db.models.deletion
import shuup.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0093_fix_attr_m2m'),
        ('givesome', '0065_auto_20211001_0846'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonationExtra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local_currency_total_value', shuup.core.fields.MoneyValueField(decimal_places=9, default=0, editable=False, max_digits=36, verbose_name='local currency total')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='donation_extra', to='shuup.Order')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

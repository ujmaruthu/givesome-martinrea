# Generated by Django 2.2.16 on 2020-11-12 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0077_remove_approved_from_supplier'),
        ('givesome', '0002_sustainabilitygoal_identifier'),
    ]

    operations = [
        migrations.CreateModel(
            name='GivesomePromotedProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promoting_suppliers', to='shuup.Product')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promoted_projects', to='shuup.Supplier')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

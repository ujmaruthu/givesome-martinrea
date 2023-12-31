# Generated by Django 2.2.16 on 2020-11-17 23:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0077_remove_approved_from_supplier'),
        ('givesome', '0008_add_website_url_field_to_vendor_extra'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorSustainabilityGoals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goals', models.ManyToManyField(blank=True, related_name='vendor_sustainability_goals', to='givesome.SustainabilityGoal', verbose_name='vendors')),
                ('vendor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_sustainability_goals', to='shuup.Supplier')),
            ],
        ),
    ]

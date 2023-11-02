# Generated by Django 2.2.16 on 2020-11-16 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0006_project_promote_related_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendorextra',
            name='vendor',
            field=models.OneToOneField(help_text='The vendor described by this extra information.', on_delete=django.db.models.deletion.CASCADE, related_name='givesome_extra', to='shuup.Supplier'),
        ),
    ]
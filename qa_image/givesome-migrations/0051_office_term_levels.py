# Generated by Django 2.2.21 on 2021-07-13 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0091_background_tasks'),
        ('givesome', '0050_fix_office_mptt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendorextra',
            name='office_term',
        ),
        migrations.CreateModel(
            name='SupplierOfficeTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(help_text='Enter a term you want to use for your offices/chapters/locations.', max_length=32, verbose_name='Office term')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='office_terms', to='shuup.Supplier')),
            ],
            options={
                'ordering': ('supplier', 'level'),
                'unique_together': {('supplier', 'level')},
            },
        ),
    ]

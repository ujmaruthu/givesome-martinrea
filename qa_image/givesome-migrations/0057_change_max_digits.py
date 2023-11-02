# Generated by Django 2.2.24 on 2021-09-01 10:34

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0056_rename_givesome_purse_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offplatformdonation',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='How much did you donate?', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='volunteerhours',
            name='hours',
            field=models.DecimalField(decimal_places=2, help_text='How many hours did you volunteer?', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
    ]
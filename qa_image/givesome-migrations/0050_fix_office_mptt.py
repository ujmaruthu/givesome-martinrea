# Generated by Django 2.2.21 on 2021-07-12 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0049_make_office_use_mptt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='givesomeoffice',
            name='level',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
        migrations.AlterField(
            model_name='givesomeoffice',
            name='lft',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
        migrations.AlterField(
            model_name='givesomeoffice',
            name='rght',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
        migrations.AlterField(
            model_name='givesomeoffice',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
    ]
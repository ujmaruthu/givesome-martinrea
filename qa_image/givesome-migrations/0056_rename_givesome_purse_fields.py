# Generated by Django 2.2.21 on 2021-07-20 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0055_add_allow_purse_to_supplier'),
    ]

    operations = [
        migrations.RenameField(
            model_name='givecardpursecharge',
            old_name='givesome_purse',
            new_name='purse',
        ),
        migrations.RenameField(
            model_name='givesomedonationdata',
            old_name='givesome_purse',
            new_name='purse',
        ),
        migrations.AlterField(
            model_name='givesomepurse',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purse', to='shuup.Shop', verbose_name='shop'),
        ),
        migrations.AlterField(
            model_name='givesomepurse',
            name='supplier',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='purse', to='shuup.Supplier', verbose_name='supplier'),
        ),
    ]

# Generated by Django 2.2.21 on 2021-07-19 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0052_add_office_disabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='givecardbatch',
            name='redirect_office',
            field=models.ForeignKey(blank=True, help_text="When user redeems a Givecard they will be redirected to this office's branded page. This field overrides `Restricted Supplier` and `Restricted Office`, and affects only redirecting. Requires selecting a `Restricted Supplier` and `Restricted Office` first, as this field contains onlysub-offices. Requires this office to be hierarchically underneath selected office on above field", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='redirect_batches', to='givesome.GivesomeOffice', verbose_name='redirect office'),
        ),
    ]
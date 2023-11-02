# Generated by Django 2.2.21 on 2021-06-22 23:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0045_add_archived_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='GivesomeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='givecardcampaign',
            name='group',
            field=models.ForeignKey(blank=True, help_text='This is used to group Campaigns to different groups in the Vendor Dashboard, with their own subtotals', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaigns', to='givesome.GivesomeGroup', verbose_name='Group'),
        ),
    ]

# Generated by Django 2.2.24 on 2022-05-30 22:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shuup', '0105_max_decimals_value'),
        ('givesome', '0069_remove_after_donation_url_create_donation_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='GivesomeCompetition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('start_date', models.DateTimeField(help_text='Start date of the competition', verbose_name='starting')),
                ('end_date', models.DateTimeField(help_text='End date of the competition', verbose_name='ending')),
                ('slug', models.SlugField(help_text='Name of competition', max_length=128, unique=True)),
                ('active', models.BooleanField(default=True, help_text='Is this competition active?', verbose_name='active')),
                ('competition_key', models.CharField(help_text='Key for customers to enter competition', max_length=64)),
                ('competition_runner', models.ForeignKey(blank=True, help_text='The vendor running the competition', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='competition_runner', to='shuup.Supplier', verbose_name='Competition Runner')),
                ('competitors', models.ManyToManyField(blank=True, help_text='Add competitors here (competitors can also join if you give them the key / link to the competition)', null=True, related_name='competitors', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

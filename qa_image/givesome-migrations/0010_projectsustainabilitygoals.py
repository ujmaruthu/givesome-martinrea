# Generated by Django 2.2.16 on 2020-11-18 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0077_remove_approved_from_supplier'),
        ('givesome', '0009_vendorsustainabilitygoals'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectSustainabilityGoals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goals', models.ManyToManyField(blank=True, related_name='project_sustainability_goals', to='givesome.SustainabilityGoal', verbose_name='projects')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='project_sustainability_goals', to='shuup.ShopProduct')),
            ],
        ),
    ]
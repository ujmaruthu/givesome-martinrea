# Generated by Django 2.2.17 on 2021-01-20 15:40
import parler.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0023_givecard_checkout_processor'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompletionVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(help_text='Paste a link to a YouTube video.', max_length=120)),
                ('linked_on', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='completion_videos', to='shuup.Product')),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
    ]
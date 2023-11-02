from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0015_add_office_model'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GivesomePromotedProduct',
        ),
    ]

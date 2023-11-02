from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('givesome', '0031_offplatformdonation_volunteerhours'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PurchaseReportData',
        ),
    ]

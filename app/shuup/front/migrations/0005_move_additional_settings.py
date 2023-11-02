from django.conf import settings
from django.db import migrations

from shuup import configuration
from shuup.front.setting_keys import (
    SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD,
    SHUUP_REGISTRATION_REQUIRES_ACTIVATION,
)


def move_settings_to_db(apps, schema_editor):

    configuration.set(
        None, SHUUP_REGISTRATION_REQUIRES_ACTIVATION, getattr(settings, "SHUUP_REGISTRATION_REQUIRES_ACTIVATION", False)
    )
    configuration.set(
        None,
        SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD,
        getattr(settings, "SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD", False),
    )


class Migration(migrations.Migration):

    dependencies = [
        ("shuup_front", "0004_move_settings_to_db"),
    ]

    operations = [migrations.RunPython(move_settings_to_db, migrations.RunPython.noop)]

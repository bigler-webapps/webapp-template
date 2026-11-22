# Required by django-core-micha >= 3.x: AbstractAuthPolicy no longer carries this field.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_authpolicy_access_code_single_use_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authpolicy',
            name='require_email_verification',
        ),
    ]

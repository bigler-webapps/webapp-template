from django.db import migrations, models


class Migration(migrations.Migration):
    """Adds AuthPolicy.admin_required_auth_factor_count.

    Reconciles drift introduced when django-core-micha extended AbstractAuthPolicy
    with this field while concrete apps were not regenerated.
    """

    dependencies = [
        ("users", "0003_authpolicy_and_profile_alignment"),
    ]

    operations = [
        migrations.AddField(
            model_name="authpolicy",
            name="admin_required_auth_factor_count",
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]

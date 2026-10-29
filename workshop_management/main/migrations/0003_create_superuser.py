from django.db import migrations


def create_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="aditapdiya@gmail.com",
            password="Admin@123",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_workshopfeedback"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(
            create_superuser,
            migrations.RunPython.noop,
        ),
    ]
# Generated by Django 5.1.3 on 2025-02-04 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0053_personal"),
    ]

    operations = [
        migrations.AddField(
            model_name="personal",
            name="contraseña_creada",
            field=models.BooleanField(default=False),
        ),
    ]

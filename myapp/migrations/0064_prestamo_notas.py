# Generated by Django 5.1.3 on 2025-03-12 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0063_personal_observacion_alter_gasto_gasto_origen"),
    ]

    operations = [
        migrations.AddField(
            model_name="prestamo",
            name="notas",
            field=models.TextField(blank=True, null=True),
        ),
    ]

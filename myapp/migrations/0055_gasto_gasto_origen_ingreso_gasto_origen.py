# Generated by Django 5.1.3 on 2025-02-05 09:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0054_personal_contraseña_creada"),
    ]

    operations = [
        migrations.AddField(
            model_name="gasto",
            name="gasto_origen",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="gastos_generados",
                to="myapp.gasto",
            ),
        ),
        migrations.AddField(
            model_name="ingreso",
            name="gasto_origen",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="ingreso_generado",
                to="myapp.gasto",
            ),
        ),
    ]

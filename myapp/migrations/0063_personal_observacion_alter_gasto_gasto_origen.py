# Generated by Django 5.1.3 on 2025-03-12 09:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0062_personal_turno_manana_fin_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="personal",
            name="observacion",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="gasto",
            name="gasto_origen",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="gastos_generados",
                to="myapp.gasto",
            ),
        ),
    ]

# Generated by Django 5.1.3 on 2025-02-19 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0059_saldoinicial_monto_saldo_inicial_yape_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ingreso",
            name="importe_efectivo",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name="ingreso",
            name="importe_yape",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]

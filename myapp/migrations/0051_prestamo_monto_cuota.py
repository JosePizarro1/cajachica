# Generated by Django 5.1.3 on 2025-01-31 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0050_gasto_prestamo_pago"),
    ]

    operations = [
        migrations.AddField(
            model_name="prestamo",
            name="monto_cuota",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]

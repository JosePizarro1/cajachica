# Generated by Django 5.1.3 on 2024-12-13 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_gasto_moneda'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingreso',
            name='fecha_operacion',
            field=models.DateField(blank=True, null=True),
        ),
    ]

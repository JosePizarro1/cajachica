# Generated by Django 5.1.3 on 2024-11-28 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_ingreso_concepto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingreso',
            name='codigo_operacion',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='ingreso',
            name='observacion',
            field=models.TextField(blank=True, null=True),
        ),
    ]

# Generated by Django 5.1.3 on 2025-01-30 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0043_prestamo_monto'),
    ]

    operations = [
        migrations.CreateModel(
            name='FichaIngreso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dni', models.CharField(blank=True, max_length=8, null=True)),
                ('nombres', models.CharField(blank=True, max_length=255, null=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('celular', models.CharField(blank=True, max_length=15, null=True)),
                ('correo_personal', models.EmailField(blank=True, max_length=254, null=True)),
                ('correo_corporativo', models.EmailField(blank=True, max_length=254, null=True)),
                ('direccion', models.TextField(blank=True, null=True)),
                ('fecha_inicio', models.DateField(blank=True, null=True)),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('tipo_trabajador', models.CharField(blank=True, max_length=100, null=True)),
                ('tipo_contrato', models.CharField(blank=True, max_length=100, null=True)),
                ('tipo_pago', models.CharField(blank=True, choices=[('efectivo', 'Efectivo'), ('deposito', 'Deposito')], max_length=10, null=True)),
                ('nombre_cuenta', models.CharField(blank=True, max_length=255, null=True)),
                ('numero_cuenta', models.CharField(blank=True, max_length=50, null=True)),
                ('asignacion_familiar', models.BooleanField(default=False)),
                ('regimen_salud', models.CharField(blank=True, choices=[('essalud', 'EsSalud'), ('sis', 'SIS')], max_length=10, null=True)),
                ('regimen_pensionario', models.CharField(blank=True, choices=[('onp', 'ONP'), ('afp', 'AFP')], max_length=10, null=True)),
                ('situacion_educativa', models.CharField(blank=True, max_length=255, null=True)),
                ('tipo_instruccion', models.CharField(blank=True, max_length=255, null=True)),
                ('institucion', models.CharField(blank=True, max_length=255, null=True)),
                ('carrera', models.CharField(blank=True, max_length=255, null=True)),
                ('anio_egreso', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
    ]

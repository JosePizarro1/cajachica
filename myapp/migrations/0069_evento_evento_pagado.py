# Generated by Django 5.1.3 on 2025-03-17 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0068_evento_prestamo'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='evento_pagado',
            field=models.BooleanField(default=False, verbose_name='Evento Pagado'),
        ),
    ]

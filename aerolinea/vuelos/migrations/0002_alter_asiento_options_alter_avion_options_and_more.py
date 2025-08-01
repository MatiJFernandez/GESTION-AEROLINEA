# Generated by Django 5.2.4 on 2025-07-27 20:09

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vuelos', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asiento',
            options={'verbose_name': 'Asiento', 'verbose_name_plural': 'Asientos'},
        ),
        migrations.AlterModelOptions(
            name='avion',
            options={'verbose_name': 'Avión', 'verbose_name_plural': 'Aviones'},
        ),
        migrations.AddField(
            model_name='avion',
            name='estado',
            field=models.CharField(choices=[('activo', 'Activo'), ('mantenimiento', 'En Mantenimiento'), ('retirado', 'Retirado')], default='activo', help_text='Estado operativo del avión', max_length=20),
        ),
        migrations.AddField(
            model_name='avion',
            name='fecha_fabricacion',
            field=models.DateField(blank=True, help_text='Fecha de fabricación del avión', null=True),
        ),
        migrations.AlterField(
            model_name='asiento',
            name='avion',
            field=models.ForeignKey(help_text='Avión al que pertenece el asiento', on_delete=django.db.models.deletion.CASCADE, related_name='asientos', to='vuelos.avion'),
        ),
        migrations.AlterField(
            model_name='asiento',
            name='columna',
            field=models.CharField(help_text='Letra de columna del asiento (A, B, C, etc.)', max_length=2),
        ),
        migrations.AlterField(
            model_name='asiento',
            name='estado',
            field=models.CharField(choices=[('disponible', 'Disponible'), ('reservado', 'Reservado'), ('ocupado', 'Ocupado'), ('en_mantenimiento', 'En Mantenimiento')], default='disponible', help_text='Estado actual del asiento', max_length=20),
        ),
        migrations.AlterField(
            model_name='asiento',
            name='fila',
            field=models.PositiveIntegerField(help_text='Número de fila del asiento', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='asiento',
            name='numero',
            field=models.CharField(help_text='Número único del asiento', max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='asiento',
            name='tipo',
            field=models.CharField(choices=[('economica', 'Económica'), ('premium', 'Premium'), ('primera', 'Primera Clase')], default='economica', help_text='Tipo de asiento', max_length=20),
        ),
        migrations.AlterField(
            model_name='avion',
            name='capacidad',
            field=models.PositiveIntegerField(help_text='Capacidad total de pasajeros', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AlterField(
            model_name='avion',
            name='columnas',
            field=models.PositiveIntegerField(help_text='Número de columnas de asientos', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)]),
        ),
        migrations.AlterField(
            model_name='avion',
            name='filas',
            field=models.PositiveIntegerField(help_text='Número de filas de asientos', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='avion',
            name='modelo',
            field=models.CharField(help_text='Modelo del avión', max_length=100),
        ),
        migrations.AlterField(
            model_name='vuelo',
            name='avion',
            field=models.ForeignKey(help_text='Avión asignado al vuelo', on_delete=django.db.models.deletion.CASCADE, related_name='vuelos', to='vuelos.avion'),
        ),
        migrations.AlterField(
            model_name='vuelo',
            name='destino',
            field=models.CharField(help_text='Ciudad de destino del vuelo', max_length=100),
        ),
        migrations.AlterField(
            model_name='vuelo',
            name='duracion',
            field=models.CharField(help_text='Duración del vuelo (formato: HH:MM)', max_length=10),
        ),
        migrations.AlterField(
            model_name='vuelo',
            name='estado',
            field=models.CharField(choices=[('programado', 'Programado'), ('en_vuelo', 'En Vuelo'), ('aterrizado', 'Aterrizado'), ('cancelado', 'Cancelado')], default='programado', help_text='Estado actual del vuelo', max_length=20),
        ),
        migrations.AlterField(
            model_name='vuelo',
            name='fecha_llegada',
            field=models.DateTimeField(help_text='Fecha y hora de llegada'),
        ),
        migrations.AlterField(
            model_name='vuelo',
            name='fecha_salida',
            field=models.DateTimeField(help_text='Fecha y hora de salida'),
        ),
        migrations.AlterField(
            model_name='vuelo',
            name='origen',
            field=models.CharField(help_text='Ciudad de origen del vuelo', max_length=100),
        ),
        migrations.AlterField(
            model_name='vuelo',
            name='precio_base',
            field=models.DecimalField(decimal_places=2, help_text='Precio base del vuelo (asiento económico)', max_digits=10),
        ),
        migrations.AddIndex(
            model_name='asiento',
            index=models.Index(fields=['avion', 'estado'], name='vuelos_asie_avion_i_063360_idx'),
        ),
        migrations.AddIndex(
            model_name='asiento',
            index=models.Index(fields=['numero'], name='vuelos_asie_numero_1d5733_idx'),
        ),
        migrations.AddIndex(
            model_name='asiento',
            index=models.Index(fields=['tipo'], name='vuelos_asie_tipo_2c7f69_idx'),
        ),
        migrations.AddIndex(
            model_name='asiento',
            index=models.Index(fields=['estado'], name='vuelos_asie_estado_57b5b7_idx'),
        ),
        migrations.AddIndex(
            model_name='avion',
            index=models.Index(fields=['modelo'], name='vuelos_avio_modelo_101882_idx'),
        ),
        migrations.AddIndex(
            model_name='avion',
            index=models.Index(fields=['estado'], name='vuelos_avio_estado_1987d2_idx'),
        ),
        migrations.AddIndex(
            model_name='avion',
            index=models.Index(fields=['capacidad'], name='vuelos_avio_capacid_f88a97_idx'),
        ),
        migrations.AddIndex(
            model_name='vuelo',
            index=models.Index(fields=['origen'], name='vuelos_vuel_origen_cf0269_idx'),
        ),
        migrations.AddIndex(
            model_name='vuelo',
            index=models.Index(fields=['destino'], name='vuelos_vuel_destino_20ec18_idx'),
        ),
        migrations.AddIndex(
            model_name='vuelo',
            index=models.Index(fields=['estado'], name='vuelos_vuel_estado_7e315b_idx'),
        ),
        migrations.AddIndex(
            model_name='vuelo',
            index=models.Index(fields=['fecha_salida'], name='vuelos_vuel_fecha_s_6b28a5_idx'),
        ),
        migrations.AddIndex(
            model_name='vuelo',
            index=models.Index(fields=['origen', 'destino'], name='vuelos_vuel_origen_f5af51_idx'),
        ),
        migrations.AddIndex(
            model_name='vuelo',
            index=models.Index(fields=['estado', 'fecha_salida'], name='vuelos_vuel_estado_55de34_idx'),
        ),
        migrations.AlterModelTable(
            name='asiento',
            table=None,
        ),
        migrations.AlterModelTable(
            name='avion',
            table=None,
        ),
        migrations.AlterModelTable(
            name='vuelo',
            table=None,
        ),
    ]

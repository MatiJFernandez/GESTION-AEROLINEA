"""
Comando personalizado para cargar datos desde archivos CSV/Excel.

Este comando permite importar datos masivos de:
- Vuelos
- Pasajeros
- Aviones
- Reservas

Uso: python manage.py cargar_datos_csv --archivo archivo.csv --tipo vuelos
"""

import csv
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import os

from vuelos.models import Vuelo, Avion, Asiento
from pasajeros.models import Pasajero
from reservas.models import Reserva
from usuarios.models import Usuario


class Command(BaseCommand):
    """
    Comando para cargar datos desde archivos CSV/Excel.
    
    Soporta múltiples tipos de datos y formatos de archivo.
    """
    
    help = 'Carga datos desde archivos CSV/Excel al sistema'
    
    def add_arguments(self, parser):
        """Define los argumentos del comando"""
        parser.add_argument(
            '--archivo',
            type=str,
            required=True,
            help='Ruta al archivo CSV/Excel a cargar'
        )
        
        parser.add_argument(
            '--tipo',
            type=str,
            required=True,
            choices=['vuelos', 'pasajeros', 'aviones', 'reservas'],
            help='Tipo de datos a cargar'
        )
        
        parser.add_argument(
            '--delimiter',
            type=str,
            default=',',
            help='Delimitador del CSV (por defecto: coma)'
        )
        
        parser.add_argument(
            '--encoding',
            type=str,
            default='utf-8',
            help='Codificación del archivo (por defecto: utf-8)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin guardar en la base de datos'
        )
    
    def handle(self, *args, **options):
        """Método principal que ejecuta el comando"""
        
        archivo = options['archivo']
        tipo = options['tipo']
        delimiter = options['delimiter']
        encoding = options['encoding']
        dry_run = options['dry_run']
        
        # Verificar que el archivo existe
        if not os.path.exists(archivo):
            raise CommandError(f'El archivo {archivo} no existe')
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Iniciando carga de {tipo} desde {archivo}')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  MODO DRY-RUN: No se guardarán datos en la base de datos')
            )
        
        try:
            # Determinar el tipo de archivo y cargar datos
            if archivo.endswith('.csv'):
                datos = self._cargar_csv(archivo, delimiter, encoding)
            elif archivo.endswith(('.xlsx', '.xls')):
                datos = self._cargar_excel(archivo)
            else:
                raise CommandError('Formato de archivo no soportado. Use CSV o Excel (.xlsx, .xls)')
            
            # Procesar datos según el tipo
            if tipo == 'vuelos':
                self._procesar_vuelos(datos, dry_run)
            elif tipo == 'pasajeros':
                self._procesar_pasajeros(datos, dry_run)
            elif tipo == 'aviones':
                self._procesar_aviones(datos, dry_run)
            elif tipo == 'reservas':
                self._procesar_reservas(datos, dry_run)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Carga de {tipo} completada exitosamente!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la carga: {str(e)}')
            )
            raise CommandError(f'Error en la carga: {str(e)}')
    
    def _cargar_csv(self, archivo, delimiter, encoding):
        """Carga datos desde un archivo CSV"""
        try:
            with open(archivo, 'r', encoding=encoding) as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                return list(reader)
        except Exception as e:
            raise CommandError(f'Error al leer CSV: {str(e)}')
    
    def _cargar_excel(self, archivo):
        """Carga datos desde un archivo Excel"""
        try:
            df = pd.read_excel(archivo)
            return df.to_dict('records')
        except Exception as e:
            raise CommandError(f'Error al leer Excel: {str(e)}')
    
    def _procesar_aviones(self, datos, dry_run):
        """Procesa datos de aviones"""
        self.stdout.write('✈️  Procesando aviones...')
        
        aviones_creados = 0
        aviones_actualizados = 0
        
        for fila in datos:
            try:
                # Validar campos requeridos
                if not all(key in fila for key in ['modelo', 'capacidad', 'filas', 'columnas']):
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Fila omitida - campos faltantes: {fila}')
                    )
                    continue
                
                modelo = fila['modelo'].strip()
                capacidad = int(fila['capacidad'])
                filas = int(fila['filas'])
                columnas = int(fila['columnas'])
                
                # Buscar avión existente o crear uno nuevo
                avion, created = Avion.objects.get_or_create(
                    modelo=modelo,
                    defaults={
                        'capacidad': capacidad,
                        'filas': filas,
                        'columnas': columnas,
                        'estado': fila.get('estado', 'activo'),
                        'fecha_fabricacion': self._parsear_fecha(fila.get('fecha_fabricacion'))
                    }
                )
                
                if not created:
                    # Actualizar avión existente
                    avion.capacidad = capacidad
                    avion.filas = filas
                    avion.columnas = columnas
                    if 'estado' in fila:
                        avion.estado = fila['estado']
                    if not dry_run:
                        avion.save()
                    aviones_actualizados += 1
                else:
                    aviones_creados += 1
                
                if not dry_run:
                    # Crear asientos automáticamente
                    self._crear_asientos_para_avion(avion)
                
                self.stdout.write(f'  ✅ Avión: {modelo} ({capacidad} asientos)')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error procesando avión: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'  📊 Resumen: {aviones_creados} creados, {aviones_actualizados} actualizados')
        )
    
    def _procesar_vuelos(self, datos, dry_run):
        """Procesa datos de vuelos"""
        self.stdout.write('🛫 Procesando vuelos...')
        
        vuelos_creados = 0
        vuelos_actualizados = 0
        
        for fila in datos:
            try:
                # Validar campos requeridos
                campos_requeridos = ['origen', 'destino', 'fecha_salida', 'fecha_llegada', 'avion_modelo']
                if not all(key in fila for key in campos_requeridos):
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Fila omitida - campos faltantes: {fila}')
                    )
                    continue
                
                origen = fila['origen'].strip()
                destino = fila['destino'].strip()
                fecha_salida = self._parsear_fecha_hora(fila['fecha_salida'])
                fecha_llegada = self._parsear_fecha_hora(fila['fecha_llegada'])
                avion_modelo = fila['avion_modelo'].strip()
                
                # Buscar avión
                try:
                    avion = Avion.objects.get(modelo=avion_modelo)
                except Avion.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Avión no encontrado: {avion_modelo}')
                    )
                    continue
                
                # Buscar vuelo existente o crear uno nuevo
                vuelo, created = Vuelo.objects.get_or_create(
                    origen=origen,
                    destino=destino,
                    fecha_salida=fecha_salida,
                    avion=avion,
                    defaults={
                        'fecha_llegada': fecha_llegada,
                        'estado': fila.get('estado', 'programado'),
                        'precio_base': float(fila.get('precio_base', 100.0)),
                        'duracion': self._calcular_duracion(fecha_salida, fecha_llegada)
                    }
                )
                
                if not created:
                    # Actualizar vuelo existente
                    vuelo.fecha_llegada = fecha_llegada
                    vuelo.estado = fila.get('estado', vuelo.estado)
                    vuelo.precio_base = float(fila.get('precio_base', vuelo.precio_base))
                    vuelo.duracion = self._calcular_duracion(fecha_salida, fecha_llegada)
                    if not dry_run:
                        vuelo.save()
                    vuelos_actualizados += 1
                else:
                    vuelos_creados += 1
                
                self.stdout.write(f'  ✅ Vuelo: {origen} → {destino} ({fecha_salida.strftime("%d/%m/%Y %H:%M")})')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error procesando vuelo: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'  📊 Resumen: {vuelos_creados} creados, {vuelos_actualizados} actualizados')
        )
    
    def _procesar_pasajeros(self, datos, dry_run):
        """Procesa datos de pasajeros"""
        self.stdout.write('👥 Procesando pasajeros...')
        
        pasajeros_creados = 0
        pasajeros_actualizados = 0
        
        for fila in datos:
            try:
                # Validar campos requeridos
                campos_requeridos = ['nombre', 'apellido', 'documento', 'email', 'fecha_nacimiento']
                if not all(key in fila for key in campos_requeridos):
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Fila omitida - campos faltantes: {fila}')
                    )
                    continue
                
                nombre = fila['nombre'].strip()
                apellido = fila['apellido'].strip()
                documento = fila['documento'].strip()
                email = fila['email'].strip()
                fecha_nacimiento = self._parsear_fecha(fila['fecha_nacimiento'])
                
                # Buscar pasajero existente o crear uno nuevo
                pasajero, created = Pasajero.objects.get_or_create(
                    documento=documento,
                    defaults={
                        'nombre': nombre,
                        'apellido': apellido,
                        'email': email,
                        'fecha_nacimiento': fecha_nacimiento,
                        'telefono': fila.get('telefono', ''),
                        'direccion': fila.get('direccion', '')
                    }
                )
                
                if not created:
                    # Actualizar pasajero existente
                    pasajero.nombre = nombre
                    pasajero.apellido = apellido
                    pasajero.email = email
                    pasajero.fecha_nacimiento = fecha_nacimiento
                    if 'telefono' in fila:
                        pasajero.telefono = fila['telefono']
                    if 'direccion' in fila:
                        pasajero.direccion = fila['direccion']
                    if not dry_run:
                        pasajero.save()
                    pasajeros_actualizados += 1
                else:
                    pasajeros_creados += 1
                
                self.stdout.write(f'  ✅ Pasajero: {nombre} {apellido} ({documento})')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error procesando pasajero: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'  📊 Resumen: {pasajeros_creados} creados, {pasajeros_actualizados} actualizados')
        )
    
    def _procesar_reservas(self, datos, dry_run):
        """Procesa datos de reservas"""
        self.stdout.write('🎫 Procesando reservas...')
        
        reservas_creadas = 0
        reservas_actualizadas = 0
        
        for fila in datos:
            try:
                # Validar campos requeridos
                campos_requeridos = ['vuelo_id', 'pasajero_documento', 'asiento_numero']
                if not all(key in fila for key in campos_requeridos):
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Fila omitida - campos faltantes: {fila}')
                    )
                    continue
                
                vuelo_id = int(fila['vuelo_id'])
                pasajero_documento = fila['pasajero_documento'].strip()
                asiento_numero = fila['asiento_numero'].strip()
                
                # Buscar vuelo
                try:
                    vuelo = Vuelo.objects.get(id=vuelo_id)
                except Vuelo.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Vuelo no encontrado: {vuelo_id}')
                    )
                    continue
                
                # Buscar pasajero
                try:
                    pasajero = Pasajero.objects.get(documento=pasajero_documento)
                except Pasajero.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Pasajero no encontrado: {pasajero_documento}')
                    )
                    continue
                
                # Buscar asiento
                try:
                    asiento = Asiento.objects.get(
                        avion=vuelo.avion,
                        numero=asiento_numero
                    )
                except Asiento.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Asiento no encontrado: {asiento_numero}')
                    )
                    continue
                
                # Verificar si ya existe la reserva
                reserva, created = Reserva.objects.get_or_create(
                    vuelo=vuelo,
                    pasajero=pasajero,
                    asiento=asiento,
                    defaults={
                        'estado': fila.get('estado', 'pendiente'),
                        'precio': float(fila.get('precio', vuelo.precio_base)),
                        'fecha_vencimiento': timezone.now() + timedelta(hours=24),
                        'observaciones': fila.get('observaciones', '')
                    }
                )
                
                if not created:
                    # Actualizar reserva existente
                    reserva.estado = fila.get('estado', reserva.estado)
                    reserva.precio = float(fila.get('precio', reserva.precio))
                    if 'observaciones' in fila:
                        reserva.observaciones = fila['observaciones']
                    if not dry_run:
                        reserva.save()
                    reservas_actualizadas += 1
                else:
                    reservas_creadas += 1
                
                self.stdout.write(f'  ✅ Reserva: Vuelo {vuelo_id} - {pasajero_documento} - Asiento {asiento_numero}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error procesando reserva: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'  📊 Resumen: {reservas_creadas} creadas, {reservas_actualizadas} actualizadas')
        )
    
    def _crear_asientos_para_avion(self, avion):
        """Crea asientos automáticamente para un avión"""
        try:
            # Eliminar asientos existentes
            avion.asientos.all().delete()
            
            # Crear nuevos asientos
            for fila in range(1, avion.filas + 1):
                for col in range(avion.columnas):
                    columna = chr(65 + col)  # A, B, C, etc.
                    numero = f"{columna}{fila}"
                    
                    # Determinar tipo de asiento
                    if fila <= 3:
                        tipo = 'primera'
                    elif fila <= 8:
                        tipo = 'premium'
                    else:
                        tipo = 'economica'
                    
                    Asiento.objects.create(
                        avion=avion,
                        numero=numero,
                        fila=fila,
                        columna=columna,
                        tipo=tipo,
                        estado='disponible'
                    )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Error creando asientos para avión {avion.modelo}: {str(e)}')
            )
    
    def _parsear_fecha(self, fecha_str):
        """Parsea una fecha desde string"""
        if not fecha_str:
            return None
        
        try:
            # Intentar diferentes formatos
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
            for formato in formatos:
                try:
                    return datetime.strptime(fecha_str, formato).date()
                except ValueError:
                    continue
            raise ValueError(f'Formato de fecha no reconocido: {fecha_str}')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Error parseando fecha {fecha_str}: {str(e)}')
            )
            return None
    
    def _parsear_fecha_hora(self, fecha_hora_str):
        """Parsea una fecha y hora desde string"""
        if not fecha_hora_str:
            return None
        
        try:
            # Intentar diferentes formatos
            formatos = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y %H:%M',
                '%d-%m-%Y %H:%M:%S',
                '%d-%m-%Y %H:%M'
            ]
            
            for formato in formatos:
                try:
                    return datetime.strptime(fecha_hora_str, formato)
                except ValueError:
                    continue
            
            raise ValueError(f'Formato de fecha/hora no reconocido: {fecha_hora_str}')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Error parseando fecha/hora {fecha_hora_str}: {str(e)}')
            )
            return None
    
    def _calcular_duracion(self, fecha_salida, fecha_llegada):
        """Calcula la duración entre dos fechas"""
        if not fecha_salida or not fecha_llegada:
            return "00:00"
        
        diferencia = fecha_llegada - fecha_salida
        horas = int(diferencia.total_seconds() // 3600)
        minutos = int((diferencia.total_seconds() % 3600) // 60)
        
        return f"{horas:02d}:{minutos:02d}" 
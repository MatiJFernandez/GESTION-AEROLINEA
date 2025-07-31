from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

from vuelos.models import Avion, Asiento, Vuelo
from pasajeros.models import Pasajero
from reservas.models import Reserva, Boleto

User = get_user_model()

class Command(BaseCommand):
    """
    Comando personalizado para poblar la base de datos con datos de ejemplo.
    
    Este comando crea:
    - Usuarios de diferentes roles
    - Aviones con sus asientos
    - Vuelos de ejemplo
    - Pasajeros de prueba
    - Reservas y boletos de ejemplo
    
    Uso: python manage.py poblar_datos
    """
    
    help = 'Pobla la base de datos con datos de ejemplo para el sistema de aerolínea'
    
    def handle(self, *args, **options):
        """Método principal que ejecuta el comando"""
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando población de datos...')
        )
        
        # Crear usuarios
        self.crear_usuarios()
        
        # Crear aviones
        self.crear_aviones()
        
        # Crear vuelos
        self.crear_vuelos()
        
        # Crear pasajeros
        self.crear_pasajeros()
        
        # Crear reservas
        self.crear_reservas()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Datos poblados exitosamente!')
        )
    
    def crear_usuarios(self):
        """Crear usuarios de diferentes roles"""
        self.stdout.write('👥 Creando usuarios...')
        
        # Usuario administrador
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@aerolinea.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('  ✅ Usuario administrador creado')
        
        # Usuario empleado
        empleado_user, created = User.objects.get_or_create(
            username='empleado',
            defaults={
                'email': 'empleado@aerolinea.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'rol': 'empleado',
                'telefono': '123456789',
            }
        )
        if created:
            empleado_user.set_password('empleado123')
            empleado_user.save()
            self.stdout.write('  ✅ Usuario empleado creado')
        
        # Usuario cliente
        cliente_user, created = User.objects.get_or_create(
            username='cliente',
            defaults={
                'email': 'cliente@email.com',
                'first_name': 'María',
                'last_name': 'González',
                'rol': 'cliente',
                'telefono': '987654321',
            }
        )
        if created:
            cliente_user.set_password('cliente123')
            cliente_user.save()
            self.stdout.write('  ✅ Usuario cliente creado')
    
    def crear_aviones(self):
        """Crear aviones con diferentes configuraciones"""
        self.stdout.write('✈️ Creando aviones...')
        
        aviones_data = [
            {
                'modelo': 'Boeing 737',
                'filas': 30,
                'columnas': 6,
            },
            {
                'modelo': 'Airbus A320',
                'filas': 25,
                'columnas': 6,
            },
            {
                'modelo': 'Boeing 777',
                'filas': 40,
                'columnas': 9,
            },
        ]
        
        for data in aviones_data:
            avion, created = Avion.objects.get_or_create(
                modelo=data['modelo'],
                defaults=data
            )
            if created:
                self.stdout.write(f"  ✅ Avión {avion.modelo} creado")
                
                # Generar asientos automáticamente
                for fila in range(1, avion.filas + 1):
                    for col in range(avion.columnas):
                        columna = chr(65 + col)  # A, B, C, etc.
                        numero = f"{avion.modelo[:3]}{columna}{fila}"  # Hacer único por avión
                        
                        # Determinar tipo de asiento
                        if fila <= 3:
                            tipo = 'primera'
                        elif fila <= 8:
                            tipo = 'premium'
                        else:
                            tipo = 'economica'
                        
                        # Verificar que el asiento no exista ya
                        if not Asiento.objects.filter(numero=numero).exists():
                            Asiento.objects.create(
                                avion=avion,
                                numero=numero,
                                fila=fila,
                                columna=columna,
                                tipo=tipo,
                                estado='disponible'
                            )
    
    def crear_vuelos(self):
        """Crear vuelos de ejemplo"""
        self.stdout.write('🛫 Creando vuelos...')
        
        aviones = list(Avion.objects.all())
        if not aviones:
            self.stdout.write(self.style.WARNING('  ⚠️ No hay aviones disponibles'))
            return
        
        rutas = [
            ('Buenos Aires', 'Córdoba'),
            ('Buenos Aires', 'Mendoza'),
            ('Córdoba', 'Buenos Aires'),
            ('Mendoza', 'Buenos Aires'),
            ('Buenos Aires', 'Bariloche'),
            ('Bariloche', 'Buenos Aires'),
        ]
        
        # Crear vuelos para los próximos 30 días
        for i in range(20):
            origen, destino = random.choice(rutas)
            avion = random.choice(aviones)
            
            # Fecha de salida (próximos 30 días)
            fecha_salida = timezone.now() + timedelta(days=random.randint(1, 30))
            
            # Duración del vuelo (1-3 horas)
            duracion_minutos = random.randint(60, 180)
            fecha_llegada = fecha_salida + timedelta(minutes=duracion_minutos)
            
            # Precio base (100-500 USD)
            precio_base = random.randint(100, 500)
            
            vuelo, created = Vuelo.objects.get_or_create(
                avion=avion,
                origen=origen,
                destino=destino,
                fecha_salida=fecha_salida,
                defaults={
                    'fecha_llegada': fecha_llegada,
                    'duracion': duracion_minutos,
                    'estado': 'programado',
                    'precio_base': precio_base,
                }
            )
            
            if created:
                self.stdout.write(
                    f"  ✅ Vuelo {origen} → {destino} creado"
                )
    
    def crear_pasajeros(self):
        """Crear pasajeros de ejemplo"""
        self.stdout.write('👤 Creando pasajeros...')
        
        pasajeros_data = [
            {
                'nombre': 'Carlos',
                'apellido': 'Rodríguez',
                'documento': '12345678',
                'email': 'carlos@email.com',
                'telefono': '111111111',
                'fecha_nacimiento': '1985-03-15',
            },
            {
                'nombre': 'Ana',
                'apellido': 'López',
                'documento': '23456789',
                'email': 'ana@email.com',
                'telefono': '222222222',
                'fecha_nacimiento': '1990-07-22',
            },
            {
                'nombre': 'Roberto',
                'apellido': 'Martínez',
                'documento': '34567890',
                'email': 'roberto@email.com',
                'telefono': '333333333',
                'fecha_nacimiento': '1978-11-08',
            },
            {
                'nombre': 'Laura',
                'apellido': 'Fernández',
                'documento': '45678901',
                'email': 'laura@email.com',
                'telefono': '444444444',
                'fecha_nacimiento': '1992-05-12',
            },
            {
                'nombre': 'Diego',
                'apellido': 'García',
                'documento': '56789012',
                'email': 'diego@email.com',
                'telefono': '555555555',
                'fecha_nacimiento': '1988-09-30',
            },
        ]
        
        for data in pasajeros_data:
            pasajero, created = Pasajero.objects.get_or_create(
                documento=data['documento'],
                defaults=data
            )
            if created:
                self.stdout.write(
                    f"  ✅ Pasajero {pasajero.get_nombre_completo()} creado"
                )
    
    def crear_reservas(self):
        """Crear reservas de ejemplo"""
        self.stdout.write('📅 Creando reservas...')
        
        vuelos = list(Vuelo.objects.filter(estado='programado'))
        pasajeros = list(Pasajero.objects.all())
        
        if not vuelos or not pasajeros:
            self.stdout.write(self.style.WARNING('  ⚠️ No hay vuelos o pasajeros disponibles'))
            return
        
        # Crear algunas reservas de ejemplo
        for i in range(10):
            vuelo = random.choice(vuelos)
            pasajero = random.choice(pasajeros)
            
            # Buscar un asiento disponible
            asientos_disponibles = vuelo.avion.asientos.filter(estado='disponible')
            if not asientos_disponibles.exists():
                continue
            
            asiento = random.choice(asientos_disponibles)
            
            # Verificar que no exista ya una reserva para este vuelo, pasajero y asiento
            if Reserva.objects.filter(vuelo=vuelo, pasajero=pasajero, asiento=asiento).exists():
                continue
            
            # Crear la reserva
            precio = vuelo.precio_base + random.randint(-50, 100)  # Variación del precio
            reserva = Reserva.objects.create(
                vuelo=vuelo,
                pasajero=pasajero,
                asiento=asiento,
                precio=precio,
                estado='confirmada',
                fecha_vencimiento=timezone.now() + timedelta(days=1)
            )
            
            # Marcar el asiento como reservado
            asiento.estado = 'reservado'
            asiento.save()
            
            # Crear boleto para algunas reservas
            if random.choice([True, False]):
                Boleto.objects.create(
                    reserva=reserva,
                    estado='emitido',
                    puerta_embarque=f"P{random.randint(1, 20)}",
                    hora_embarque=(
                        vuelo.fecha_salida - timedelta(minutes=30)
                    ).time()
                )
            
            self.stdout.write(
                f"  ✅ Reserva creada: {pasajero.get_nombre_completo()} - {vuelo.origen} → {vuelo.destino}"
            ) 
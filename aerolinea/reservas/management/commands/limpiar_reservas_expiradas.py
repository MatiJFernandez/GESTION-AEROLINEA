"""
Comando de gestión para limpiar reservas expiradas.

Este comando se ejecuta automáticamente para liberar asientos
de reservas que han expirado sin confirmación.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from reservas.models import Reserva
from vuelos.models import Asiento


class Command(BaseCommand):
    help = 'Limpia reservas expiradas y libera asientos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se haría sin ejecutar cambios',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar limpieza incluso de reservas recientes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        # Obtener reservas expiradas
        if force:
            # Limpiar todas las reservas pendientes expiradas
            reservas_expiradas = Reserva.objects.filter(
                estado='pendiente',
                fecha_vencimiento__lt=timezone.now()
            )
        else:
            # Limpiar solo reservas expiradas por más de 1 hora
            una_hora_atras = timezone.now() - timezone.timedelta(hours=1)
            reservas_expiradas = Reserva.objects.filter(
                estado='pendiente',
                fecha_vencimiento__lt=una_hora_atras
            )
        
        count = reservas_expiradas.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay reservas expiradas para limpiar.')
            )
            return
        
        self.stdout.write(f'Encontradas {count} reservas expiradas.')
        
        if dry_run:
            self.stdout.write('MODO DRY-RUN: No se realizarán cambios.')
            for reserva in reservas_expiradas:
                self.stdout.write(
                    f'  - Reserva {reserva.codigo_reserva} expiró el {reserva.fecha_vencimiento}'
                )
            return
        
        # Procesar reservas expiradas
        reservas_limpiadas = 0
        asientos_liberados = 0
        
        try:
            with transaction.atomic():
                for reserva in reservas_expiradas:
                    # Marcar reserva como cancelada
                    reserva.estado = 'cancelada'
                    reserva.save()
                    
                    # Liberar asiento si está reservado
                    if reserva.asiento.estado == 'reservado':
                        reserva.asiento.estado = 'disponible'
                        reserva.asiento.save()
                        asientos_liberados += 1
                    
                    reservas_limpiadas += 1
                    
                    self.stdout.write(
                        f'  - Reserva {reserva.codigo_reserva} cancelada, asiento {reserva.asiento.numero} liberado'
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Limpieza completada: {reservas_limpiadas} reservas canceladas, '
                    f'{asientos_liberados} asientos liberados.'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error durante la limpieza: {str(e)}')
            ) 
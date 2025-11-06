"""
Signals para la aplicación vuelos.

Este archivo define los signals que se disparan cuando ocurren eventos
específicos en los modelos de vuelos.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Vuelo, Avion, Asiento


@receiver(post_save, sender=Vuelo)
def vuelo_creado_actualizado(sender, instance, created, **kwargs):
    """
    Signal que se dispara cuando se crea o actualiza un vuelo.
    
    Args:
        sender: Modelo que disparó el signal
        instance: Instancia del modelo
        created: True si se creó, False si se actualizó
        **kwargs: Argumentos adicionales
    """
    if created:
        # Lógica cuando se crea un nuevo vuelo
        print(f"Nuevo vuelo creado: {instance}")
        
        # Enviar notificación por email (opcional)
        # send_mail(
        #     subject='Nuevo vuelo programado',
        #     message=f'Se ha programado un nuevo vuelo: {instance}',
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=['admin@aerolinea.com'],
        # )
    
    else:
        # Lógica cuando se actualiza un vuelo
        print(f"Vuelo actualizado: {instance}")
        
        # Si el estado cambió a 'en_vuelo', notificar
        if instance.estado == 'en_vuelo':
            print(f"Vuelo {instance} ha despegado")


@receiver(post_save, sender=Avion)
def avion_creado_actualizado(sender, instance, created, **kwargs):
    """
    Signal que se dispara cuando se crea o actualiza un avión.
    
    Args:
        sender: Modelo que disparó el signal
        instance: Instancia del modelo
        created: True si se creó, False si se actualizó
        **kwargs: Argumentos adicionales
    """
    if created:
        print(f"Nuevo avión registrado: {instance}")
        
        # Crear asientos automáticamente para el nuevo avión
        from .services.vuelos import AsientoService
        asiento_service = AsientoService()
        asientos_creados = asiento_service.crear_asientos_para_avion(instance.id)
        print(f"Se crearon {len(asientos_creados)} asientos para el avión {instance}")
    
    else:
        print(f"Avión actualizado: {instance}")
        
        # Si el estado cambió a 'mantenimiento', notificar
        if instance.estado == 'mantenimiento':
            print(f"Avión {instance} enviado a mantenimiento")


@receiver(post_save, sender=Asiento)
def asiento_creado_actualizado(sender, instance, created, **kwargs):
    """
    Signal que se dispara cuando se crea o actualiza un asiento.
    
    Args:
        sender: Modelo que disparó el signal
        instance: Instancia del modelo
        created: True si se creó, False si se actualizó
        **kwargs: Argumentos adicionales
    """
    if created:
        print(f"Nuevo asiento creado: {instance}")
    
    else:
        print(f"Asiento actualizado: {instance}")
        
        # Si el estado cambió a 'reservado', registrar la acción
        if instance.estado == 'reservado':
            print(f"Asiento {instance} reservado")


@receiver(post_delete, sender=Vuelo)
def vuelo_eliminado(sender, instance, **kwargs):
    """
    Signal que se dispara cuando se elimina un vuelo.
    
    Args:
        sender: Modelo que disparó el signal
        instance: Instancia del modelo
        **kwargs: Argumentos adicionales
    """
    print(f"Vuelo eliminado: {instance}")
    
    # Notificar a los pasajeros que tenían reservas en este vuelo
    # (implementación opcional)


@receiver(pre_save, sender=Vuelo)
def validar_vuelo_antes_guardar(sender, instance, **kwargs):
    """
    Signal que se dispara antes de guardar un vuelo.
    
    Args:
        sender: Modelo que disparó el signal
        instance: Instancia del modelo
        **kwargs: Argumentos adicionales
    """
    from django.core.exceptions import ValidationError
    
    # Validaciones adicionales antes de guardar
    if instance.fecha_salida and instance.fecha_llegada:
        if instance.fecha_llegada <= instance.fecha_salida:
            raise ValidationError("La fecha de llegada debe ser posterior a la de salida")
    
    if instance.precio_base and instance.precio_base <= 0:
        raise ValidationError("El precio debe ser mayor a 0")


@receiver(post_save, sender=Vuelo)
def actualizar_estadisticas_vuelos(sender, instance, **kwargs):
    """
    Signal para actualizar estadísticas de vuelos.
    
    Args:
        sender: Modelo que disparó el signal
        instance: Instancia del modelo
        **kwargs: Argumentos adicionales
    """
    # Actualizar estadísticas en caché o base de datos
    from django.core.cache import cache
    
    # Actualizar contador de vuelos activos
    vuelos_activos = Vuelo.objects.filter(estado='programado').count()
    cache.set('vuelos_activos_count', vuelos_activos, 300)  # 5 minutos
    
    # Actualizar contador total de vuelos
    total_vuelos = Vuelo.objects.count()
    cache.set('total_vuelos_count', total_vuelos, 300)  # 5 minutos 
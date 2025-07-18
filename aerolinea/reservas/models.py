from django.db import models
import uuid
from datetime import datetime

# Create your models here.

class Reserva(models.Model):
    """
    Modelo que representa una reserva de vuelo en el sistema.
    
    Una reserva es la relación entre un pasajero, un vuelo y un asiento,
    con información adicional sobre el estado y precio de la reserva.
    """
    
    # Relaciones con otros modelos
    vuelo = models.ForeignKey(
        'vuelos.Vuelo',  # Referencia al modelo Vuelo en la app vuelos
        on_delete=models.CASCADE,  # Si se elimina el vuelo, se elimina la reserva
        related_name='reservas',   # Permite acceder desde vuelo.reservas.all()
        help_text='Vuelo reservado'
    )
    
    pasajero = models.ForeignKey(
        'pasajeros.Pasajero',  # Referencia al modelo Pasajero en la app pasajeros
        on_delete=models.CASCADE,  # Si se elimina el pasajero, se elimina la reserva
        related_name='reservas',   # Permite acceder desde pasajero.reservas.all()
        help_text='Pasajero que realiza la reserva'
    )
    
    asiento = models.ForeignKey(
        'vuelos.Asiento',  # Referencia al modelo Asiento en la app vuelos
        on_delete=models.CASCADE,  # Si se elimina el asiento, se elimina la reserva
        related_name='reservas',   # Permite acceder desde asiento.reservas.all()
        help_text='Asiento reservado'
    )
    
    # Código único de reserva (generado automáticamente)
    codigo_reserva = models.CharField(
        max_length=10,
        unique=True,
        default=uuid.uuid4,
        help_text='Código único de la reserva'
    )
    
    # Estado de la reserva
    ESTADOS_RESERVA = [
        ('confirmada', 'Confirmada'),
        ('pendiente', 'Pendiente de Pago'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
        ('expirada', 'Expirada'),
    ]
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_RESERVA,
        default='pendiente',
        help_text='Estado actual de la reserva'
    )
    
    # Información temporal
    fecha_reserva = models.DateTimeField(
        auto_now_add=True,  # Se establece automáticamente al crear
        help_text='Fecha y hora en que se realizó la reserva'
    )
    
    fecha_vencimiento = models.DateTimeField(
        help_text='Fecha límite para confirmar la reserva'
    )
    
    # Información económica
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio final de la reserva'
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones adicionales sobre la reserva'
    )
    
    # Metadatos del modelo
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        db_table = 'reservas'
        # Ordenar por fecha de reserva (más recientes primero)
        ordering = ['-fecha_reserva']
        # Una reserva debe ser única por vuelo, pasajero y asiento
        unique_together = ['vuelo', 'pasajero', 'asiento']
    
    def __str__(self):
        """Representación en string de la reserva"""
        return f"Reserva {self.codigo_reserva} - {self.pasajero.get_nombre_completo()}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para generar código único"""
        if not self.codigo_reserva:
            # Generar código único de 8 caracteres
            self.codigo_reserva = str(uuid.uuid4())[:8].upper()
        
        if not self.fecha_vencimiento:
            # Establecer vencimiento en 24 horas por defecto
            from datetime import timedelta
            self.fecha_vencimiento = datetime.now() + timedelta(hours=24)
        
        super().save(*args, **kwargs)
    
    def esta_confirmada(self):
        """Verifica si la reserva está confirmada"""
        return self.estado == 'confirmada'
    
    def esta_vencida(self):
        """Verifica si la reserva está vencida"""
        return datetime.now() > self.fecha_vencimiento
    
    def puede_cancelar(self):
        """Verifica si la reserva puede ser cancelada"""
        return self.estado in ['confirmada', 'pendiente']
    
    def get_resumen(self):
        """Retorna un resumen de la reserva"""
        return {
            'codigo': self.codigo_reserva,
            'pasajero': self.pasajero.get_nombre_completo(),
            'vuelo': self.vuelo.get_ruta(),
            'asiento': self.asiento.numero,
            'precio': self.precio,
            'estado': self.get_estado_display()
        }


class Boleto(models.Model):
    """
    Modelo que representa un boleto de vuelo emitido.
    
    Un boleto es un documento oficial que se genera a partir de una
    reserva confirmada y permite al pasajero abordar el vuelo.
    """
    
    # Relación uno a uno con la reserva
    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.CASCADE,  # Si se elimina la reserva, se elimina el boleto
        related_name='boleto',     # Permite acceder desde reserva.boleto
        help_text='Reserva asociada a este boleto'
    )
    
    # Código de barras único del boleto
    codigo_barra = models.CharField(
        max_length=50,
        unique=True,
        help_text='Código de barras único del boleto'
    )
    
    # Fecha de emisión del boleto
    fecha_emision = models.DateTimeField(
        auto_now_add=True,  # Se establece automáticamente al crear
        help_text='Fecha y hora de emisión del boleto'
    )
    
    # Estado del boleto
    ESTADOS_BOLETO = [
        ('emitido', 'Emitido'),
        ('usado', 'Usado'),
        ('cancelado', 'Cancelado'),
        ('perdido', 'Perdido'),
    ]
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_BOLETO,
        default='emitido',
        help_text='Estado actual del boleto'
    )
    
    # Información adicional
    puerta_embarque = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Puerta de embarque asignada'
    )
    
    hora_embarque = models.TimeField(
        blank=True,
        null=True,
        help_text='Hora de embarque'
    )
    
    # Metadatos del modelo
    class Meta:
        verbose_name = 'Boleto'
        verbose_name_plural = 'Boletos'
        db_table = 'boletos'
        # Ordenar por fecha de emisión (más recientes primero)
        ordering = ['-fecha_emision']
    
    def __str__(self):
        """Representación en string del boleto"""
        return f"Boleto {self.codigo_barra} - {self.reserva.pasajero.get_nombre_completo()}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para generar código de barras"""
        if not self.codigo_barra:
            # Generar código de barras único
            self.codigo_barra = f"BOL{str(uuid.uuid4())[:12].upper()}"
        super().save(*args, **kwargs)
    
    def esta_activo(self):
        """Verifica si el boleto está activo"""
        return self.estado == 'emitido'
    
    def puede_usar(self):
        """Verifica si el boleto puede ser usado"""
        return self.estado == 'emitido' and self.reserva.esta_confirmada()
    
    def marcar_como_usado(self):
        """Marca el boleto como usado"""
        self.estado = 'usado'
        self.save()
    
    def get_informacion_vuelo(self):
        """Retorna información del vuelo asociado"""
        vuelo = self.reserva.vuelo
        return {
            'origen': vuelo.origen,
            'destino': vuelo.destino,
            'fecha_salida': vuelo.fecha_salida,
            'asiento': self.reserva.asiento.numero,
            'puerta': self.puerta_embarque,
            'hora_embarque': self.hora_embarque
        }

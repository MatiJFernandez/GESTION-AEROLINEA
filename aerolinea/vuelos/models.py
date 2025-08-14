"""
Modelos para la aplicación vuelos.

Este archivo define los modelos relacionados con:
- Aviones
- Asientos
- Vuelos
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Avion(models.Model):
    """
    Modelo para representar un avión.
    
    Contiene información básica del avión como modelo, capacidad,
    y configuración de asientos.
    """
    modelo = models.CharField(max_length=100, help_text="Modelo del avión")
    capacidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text="Capacidad total de pasajeros"
    )
    filas = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Número de filas de asientos"
    )
    columnas = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Número de columnas de asientos"
    )
    fecha_fabricacion = models.DateField(
        null=True, blank=True,
        help_text="Fecha de fabricación del avión"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('mantenimiento', 'En Mantenimiento'),
            ('retirado', 'Retirado'),
        ],
        default='activo',
        help_text="Estado operativo del avión"
    )
    
    class Meta:
        verbose_name = "Avión"
        verbose_name_plural = "Aviones"
        # Índices para optimizar consultas frecuentes
        indexes = [
            models.Index(fields=['modelo']),
            models.Index(fields=['estado']),
            models.Index(fields=['capacidad']),
        ]
    
    def __str__(self):
        return f"{self.modelo} ({self.capacidad} asientos)"
    
    def calcular_capacidad(self):
        """Calcula la capacidad basada en filas y columnas."""
        return self.filas * self.columnas
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para actualizar capacidad automáticamente."""
        if not self.capacidad:
            self.capacidad = self.calcular_capacidad()
        super().save(*args, **kwargs)


class Asiento(models.Model):
    """
    Modelo para representar un asiento en un avión.
    
    Cada asiento pertenece a un avión específico y tiene
    una posición única (fila y columna).
    """
    avion = models.ForeignKey(
        Avion, on_delete=models.CASCADE, related_name='asientos',
        help_text="Avión al que pertenece el asiento"
    )
    numero = models.CharField(
        max_length=10, unique=True,
        help_text="Número único del asiento"
    )
    fila = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Número de fila del asiento"
    )
    columna = models.CharField(
        max_length=2,
        help_text="Letra de columna del asiento (A, B, C, etc.)"
    )
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('economica', 'Económica'),
            ('premium', 'Premium'),
            ('primera', 'Primera Clase'),
        ],
        default='economica',
        help_text="Tipo de asiento"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('disponible', 'Disponible'),
            ('reservado', 'Reservado'),
            ('ocupado', 'Ocupado'),
            ('en_mantenimiento', 'En Mantenimiento'),
        ],
        default='disponible',
        help_text="Estado actual del asiento"
    )
    
    class Meta:
        verbose_name = "Asiento"
        verbose_name_plural = "Asientos"
        unique_together = ['avion', 'fila', 'columna']
        # Índices para optimizar consultas frecuentes
        indexes = [
            models.Index(fields=['avion', 'estado']),
            models.Index(fields=['numero']),
            models.Index(fields=['tipo']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.numero} ({self.avion.modelo})"
    
    def get_tipo_display(self):
        """Retorna el nombre legible del tipo de asiento."""
        tipos = dict(self._meta.get_field('tipo').choices)
        return tipos.get(self.tipo, self.tipo)
    
    def get_estado_display(self):
        """Retorna el nombre legible del estado del asiento."""
        estados = dict(self._meta.get_field('estado').choices)
        return estados.get(self.estado, self.estado)


class Vuelo(models.Model):
    """
    Modelo para representar un vuelo.
    
    Cada vuelo tiene un avión asignado, ruta (origen-destino),
    fechas y estado operativo.
    """
    avion = models.ForeignKey(
        Avion, on_delete=models.CASCADE, related_name='vuelos',
        help_text="Avión asignado al vuelo"
    )
    origen = models.CharField(
        max_length=100,
        help_text="Ciudad de origen del vuelo"
    )
    destino = models.CharField(
        max_length=100,
        help_text="Ciudad de destino del vuelo"
    )
    fecha_salida = models.DateTimeField(
        help_text="Fecha y hora de salida"
    )
    fecha_llegada = models.DateTimeField(
        help_text="Fecha y hora de llegada"
    )
    duracion = models.CharField(
        max_length=10,
        help_text="Duración del vuelo (formato: HH:MM)"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('programado', 'Programado'),
            ('en_vuelo', 'En Vuelo'),
            ('aterrizado', 'Aterrizado'),
            ('cancelado', 'Cancelado'),
        ],
        default='programado',
        help_text="Estado actual del vuelo"
    )
    precio_base = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Precio base del vuelo (asiento económico)"
    )
    
    class Meta:
        verbose_name = "Vuelo"
        verbose_name_plural = "Vuelos"
        ordering = ['fecha_salida']
        # Índices para optimizar consultas frecuentes
        indexes = [
            models.Index(fields=['origen']),
            models.Index(fields=['destino']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_salida']),
            models.Index(fields=['origen', 'destino']),
            models.Index(fields=['estado', 'fecha_salida']),
        ]
    
    def __str__(self):
        return f"Vuelo {self.id}: {self.origen} → {self.destino}"
    
    def get_estado_display(self):
        """Retorna el nombre legible del estado del vuelo."""
        estados = dict(self._meta.get_field('estado').choices)
        return estados.get(self.estado, self.estado)
    
    def es_futuro(self):
        """Verifica si el vuelo es futuro."""
        from django.utils import timezone
        return self.fecha_salida > timezone.now()
    
    def calcular_precio_asiento(self, tipo_asiento):
        """
        Calcula el precio según el tipo de asiento.
        
        Args:
            tipo_asiento: 'economica', 'premium', 'primera'
        
        Returns:
            Precio calculado para el tipo de asiento
        """
        from decimal import Decimal
        multiplicadores = {
            'economica': Decimal('1.0'),
            'premium': Decimal('1.5'),
            'primera': Decimal('2.0'),
        }
        
        multiplicador = multiplicadores.get(tipo_asiento, Decimal('1.0'))
        return self.precio_base * multiplicador

from django.db import models

# Create your models here.

class Pasajero(models.Model):
    """
    Modelo que representa un pasajero en el sistema de la aerolínea.
    
    Un pasajero es una persona que puede realizar reservas y viajar
    en los vuelos de la aerolínea.
    """
    
    # Información personal del pasajero
    nombre = models.CharField(
        max_length=100,
        help_text='Nombre completo del pasajero'
    )
    
    apellido = models.CharField(
        max_length=100,
        help_text='Apellido completo del pasajero'
    )
    
    # Documento de identidad
    documento = models.CharField(
        max_length=20,
        unique=True,
        help_text='Número de documento de identidad (DNI, pasaporte, etc.)'
    )
    
    # Información de contacto
    email = models.EmailField(
        help_text='Dirección de correo electrónico del pasajero'
    )
    
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Número de teléfono del pasajero'
    )
    
    # Información personal
    fecha_nacimiento = models.DateField(
        help_text='Fecha de nacimiento del pasajero'
    )
    
    # Información adicional
    direccion = models.TextField(
        blank=True,
        null=True,
        help_text='Dirección completa del pasajero'
    )
    
    # Metadatos del modelo
    class Meta:
        verbose_name = 'Pasajero'
        verbose_name_plural = 'Pasajeros'
        db_table = 'pasajeros'
        # Ordenar por apellido y nombre
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        """Representación en string del pasajero"""
        return f"{self.apellido}, {self.nombre} - {self.documento}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del pasajero"""
        return f"{self.nombre} {self.apellido}"
    
    def get_edad(self):
        """Calcula la edad del pasajero"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    def es_mayor_de_edad(self):
        """Verifica si el pasajero es mayor de edad"""
        return self.get_edad() >= 18

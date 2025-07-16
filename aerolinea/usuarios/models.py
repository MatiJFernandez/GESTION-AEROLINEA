from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que extiende AbstractUser de Django.
    
    AbstractUser ya incluye campos como: username, email, first_name, last_name,
    password, is_active, is_staff, is_superuser, date_joined, last_login
    """
    
    # Opciones para el campo rol
    ROLES = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente', 'Cliente'),
    ]
    
    # Campos adicionales al modelo base de Django
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='cliente',
        help_text='Rol del usuario en el sistema'
    )
    
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Número de teléfono del usuario'
    )
    
    # Metadatos del modelo
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'
    
    def __str__(self):
        """Representación en string del usuario"""
        return f"{self.get_full_name()} ({self.username})"
    
    def get_rol_display(self):
        """Obtiene el nombre legible del rol"""
        return dict(self.ROLES)[self.rol]

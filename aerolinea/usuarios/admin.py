from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Register your models here.

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración personalizada del admin para el modelo Usuario.
    
    Extiende UserAdmin de Django para mantener toda la funcionalidad
    del admin de usuarios pero con nuestros campos personalizados.
    """
    
    # Campos que se mostrarán en la lista de usuarios
    list_display = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'rol', 
        'is_active', 
        'date_joined'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'rol', 
        'is_active', 
        'is_staff', 
        'date_joined'
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'telefono'
    ]
    
    # Ordenamiento por defecto
    ordering = ['-date_joined']
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        # Sección personalizada para nuestros campos
        ('Información Personalizada', {
            'fields': ('rol', 'telefono')
        }),
    )
    
    # Campos que se mostrarán al crear un nuevo usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Personalizada', {
            'fields': ('rol', 'telefono')
        }),
    )
    
    # Acciones personalizadas
    actions = ['activar_usuarios', 'desactivar_usuarios']
    
    def activar_usuarios(self, request, queryset):
        """Acción para activar usuarios seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'{updated} usuario(s) han sido activado(s) exitosamente.'
        )
    activar_usuarios.short_description = "Activar usuarios seleccionados"
    
    def desactivar_usuarios(self, request, queryset):
        """Acción para desactivar usuarios seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'{updated} usuario(s) han sido desactivado(s) exitosamente.'
        )
    desactivar_usuarios.short_description = "Desactivar usuarios seleccionados"

from django.contrib import admin
from .models import Pasajero

# Register your models here.

@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para el modelo Pasajero.
    
    Permite gestionar la información de los pasajeros con filtros
    y búsquedas útiles para la administración.
    """
    
    # Campos que se mostrarán en la lista de pasajeros
    list_display = [
        'get_nombre_completo', 
        'documento', 
        'email', 
        'telefono', 
        'get_edad', 
        'es_mayor_de_edad'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'fecha_nacimiento'
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'nombre', 
        'apellido', 
        'documento', 
        'email'
    ]
    
    # Ordenamiento por defecto
    ordering = ['apellido', 'nombre']
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'documento', 'fecha_nacimiento')
        }),
        ('Información de Contacto', {
            'fields': ('email', 'telefono')
        }),
        ('Información Adicional', {
            'fields': ('direccion',),
            'classes': ('collapse',)  # Sección colapsable
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['get_edad', 'es_mayor_de_edad']
    
    # Acciones personalizadas
    actions = ['exportar_contactos']
    
    def exportar_contactos(self, request, queryset):
        """Acción para exportar información de contacto de pasajeros"""
        # Esta es una acción de ejemplo - en un proyecto real
        # podrías generar un archivo CSV o Excel
        count = queryset.count()
        self.message_user(
            request, 
            f'Se preparó la exportación de {count} pasajero(s)'
        )
    exportar_contactos.short_description = "Exportar información de contacto"

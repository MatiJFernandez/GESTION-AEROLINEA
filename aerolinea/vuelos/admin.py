from django.contrib import admin
from .models import Avion, Asiento, Vuelo

# Register your models here.

class AsientoInline(admin.TabularInline):
    """
    Inline para mostrar los asientos dentro del admin del avión.
    
    Permite crear y editar asientos directamente desde la página del avión,
    lo que es muy útil para la gestión de la configuración de asientos.
    """
    model = Asiento
    extra = 0  # No mostrar campos vacíos por defecto
    fields = ['numero', 'fila', 'columna', 'tipo', 'estado']
    readonly_fields = ['numero']  # El número se genera automáticamente
    
    def get_queryset(self, request):
        """Optimizar la consulta para cargar solo los campos necesarios"""
        return super().get_queryset(request).select_related('avion')


@admin.register(Avion)
class AvionAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para el modelo Avión.
    
    Incluye inlines para gestionar los asientos del avión
    y personalizaciones para una mejor experiencia de usuario.
    """
    
    # Inlines para mostrar asientos
    inlines = [AsientoInline]
    
    # Campos que se mostrarán en la lista de aviones
    list_display = [
        'modelo', 
        'capacidad', 
        'filas', 
        'columnas', 
        'get_asientos_disponibles'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = ['modelo']
    
    # Campos por los que se puede buscar
    search_fields = ['modelo']
    
    # Ordenamiento por defecto
    ordering = ['modelo']
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('modelo',)
        }),
        ('Configuración de Asientos', {
            'fields': ('filas', 'columnas'),
            'description': 'La capacidad se calculará automáticamente'
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['capacidad']
    
    # Acciones personalizadas
    actions = ['generar_asientos']
    
    def get_asientos_disponibles(self, obj):
        """Mostrar cantidad de asientos disponibles"""
        return obj.asientos.filter(estado='disponible').count()
    get_asientos_disponibles.short_description = 'Asientos Disponibles'
    
    def generar_asientos(self, request, queryset):
        """Acción para generar asientos automáticamente para los aviones seleccionados"""
        for avion in queryset:
            # Eliminar asientos existentes
            avion.asientos.all().delete()
            
            # Generar nuevos asientos
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
            
            self.message_user(
                request, 
                f'Se generaron {avion.capacidad} asientos para el avión {avion.modelo}'
            )
    generar_asientos.short_description = "Generar asientos automáticamente"


@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para el modelo Asiento.
    
    Permite gestionar asientos individuales con filtros y búsquedas avanzadas.
    """
    
    # Campos que se mostrarán en la lista de asientos
    list_display = [
        'numero', 
        'avion', 
        'fila', 
        'columna', 
        'tipo', 
        'estado'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'avion', 
        'tipo', 
        'estado'
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'numero', 
        'avion__modelo'
    ]
    
    # Ordenamiento por defecto
    ordering = ['avion', 'fila', 'columna']
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = (
        ('Información del Asiento', {
            'fields': ('avion', 'numero', 'fila', 'columna')
        }),
        ('Configuración', {
            'fields': ('tipo', 'estado')
        }),
    )
    
    # Acciones personalizadas
    actions = ['marcar_disponible', 'marcar_ocupado']
    
    def marcar_disponible(self, request, queryset):
        """Acción para marcar asientos como disponibles"""
        updated = queryset.update(estado='disponible')
        self.message_user(
            request, 
            f'{updated} asiento(s) marcado(s) como disponible(s)'
        )
    marcar_disponible.short_description = "Marcar como disponible"
    
    def marcar_ocupado(self, request, queryset):
        """Acción para marcar asientos como ocupados"""
        updated = queryset.update(estado='ocupado')
        self.message_user(
            request, 
            f'{updated} asiento(s) marcado(s) como ocupado(s)'
        )
    marcar_ocupado.short_description = "Marcar como ocupado"


@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para el modelo Vuelo.
    
    Permite gestionar vuelos con información detallada y filtros útiles.
    """
    
    # Campos que se mostrarán en la lista de vuelos
    list_display = [
        'origen', 
        'destino', 
        'avion', 
        'fecha_salida', 
        'fecha_llegada', 
        'duracion', 
        'estado', 
        'precio_base'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'estado', 
        'avion', 
        'fecha_salida'
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'origen', 
        'destino', 
        'avion__modelo'
    ]
    
    # Ordenamiento por defecto
    ordering = ['fecha_salida']
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = (
        ('Información del Vuelo', {
            'fields': ('avion', 'origen', 'destino')
        }),
        ('Fechas y Horarios', {
            'fields': ('fecha_salida', 'fecha_llegada')
        }),
        ('Información Adicional', {
            'fields': ('estado', 'precio_base')
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['duracion']
    
    # Acciones personalizadas
    actions = ['cancelar_vuelos', 'activar_vuelos']
    
    def cancelar_vuelos(self, request, queryset):
        """Acción para cancelar vuelos seleccionados"""
        updated = queryset.update(estado='cancelado')
        self.message_user(
            request, 
            f'{updated} vuelo(s) cancelado(s) exitosamente'
        )
    cancelar_vuelos.short_description = "Cancelar vuelos seleccionados"
    
    def activar_vuelos(self, request, queryset):
        """Acción para activar vuelos seleccionados"""
        updated = queryset.update(estado='programado')
        self.message_user(
            request, 
            f'{updated} vuelo(s) activado(s) exitosamente'
        )
    activar_vuelos.short_description = "Activar vuelos seleccionados"

from django.contrib import admin
from .models import Reserva, Boleto

# Register your models here.

class BoletoInline(admin.StackedInline):
    """
    Inline para mostrar el boleto asociado a una reserva.
    
    Permite gestionar el boleto directamente desde la página de la reserva,
    manteniendo la relación uno a uno entre reserva y boleto.
    """
    model = Boleto
    extra = 0
    fields = ['codigo_barra', 'estado', 'puerta_embarque', 'hora_embarque']
    readonly_fields = ['codigo_barra', 'fecha_emision']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para el modelo Reserva.
    
    Incluye inlines para gestionar el boleto asociado y
    personalizaciones para una mejor gestión de reservas.
    """
    
    # Inlines para mostrar boleto
    inlines = [BoletoInline]
    
    # Campos que se mostrarán en la lista de reservas
    list_display = [
        'codigo_reserva', 
        'pasajero', 
        'vuelo', 
        'asiento', 
        'precio', 
        'estado', 
        'fecha_reserva'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'estado', 
        'fecha_reserva', 
        'vuelo__origen', 
        'vuelo__destino'
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'codigo_reserva', 
        'pasajero__nombre', 
        'pasajero__apellido', 
        'pasajero__documento'
    ]
    
    # Ordenamiento por defecto
    ordering = ['-fecha_reserva']
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = (
        ('Información de la Reserva', {
            'fields': ('codigo_reserva', 'estado', 'fecha_reserva', 'fecha_vencimiento')
        }),
        ('Detalles del Viaje', {
            'fields': ('vuelo', 'pasajero', 'asiento')
        }),
        ('Información Económica', {
            'fields': ('precio',)
        }),
        ('Información Adicional', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['codigo_reserva', 'fecha_reserva']
    
    # Acciones personalizadas
    actions = ['confirmar_reservas', 'cancelar_reservas', 'marcar_completadas']
    
    def confirmar_reservas(self, request, queryset):
        """Acción para confirmar reservas seleccionadas"""
        updated = queryset.update(estado='confirmada')
        self.message_user(
            request, 
            f'{updated} reserva(s) confirmada(s) exitosamente'
        )
    confirmar_reservas.short_description = "Confirmar reservas seleccionadas"
    
    def cancelar_reservas(self, request, queryset):
        """Acción para cancelar reservas seleccionadas"""
        updated = queryset.update(estado='cancelada')
        self.message_user(
            request, 
            f'{updated} reserva(s) cancelada(s) exitosamente'
        )
    cancelar_reservas.short_description = "Cancelar reservas seleccionadas"
    
    def marcar_completadas(self, request, queryset):
        """Acción para marcar reservas como completadas"""
        updated = queryset.update(estado='completada')
        self.message_user(
            request, 
            f'{updated} reserva(s) marcada(s) como completada(s)'
        )
    marcar_completadas.short_description = "Marcar como completadas"


@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para el modelo Boleto.
    
    Permite gestionar boletos individuales con información
    detallada del vuelo y el pasajero.
    """
    
    # Campos que se mostrarán en la lista de boletos
    list_display = [
        'codigo_barra', 
        'reserva', 
        'get_pasajero', 
        'get_vuelo', 
        'estado', 
        'fecha_emision'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'estado', 
        'fecha_emision'
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'codigo_barra', 
        'reserva__pasajero__nombre', 
        'reserva__pasajero__apellido'
    ]
    
    # Ordenamiento por defecto
    ordering = ['-fecha_emision']
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = (
        ('Información del Boleto', {
            'fields': ('reserva', 'codigo_barra', 'estado')
        }),
        ('Información de Embarque', {
            'fields': ('puerta_embarque', 'hora_embarque')
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['codigo_barra', 'fecha_emision']
    
    # Acciones personalizadas
    actions = ['marcar_usado', 'marcar_perdido']
    
    def get_pasajero(self, obj):
        """Mostrar nombre del pasajero"""
        return obj.reserva.pasajero.get_nombre_completo()
    get_pasajero.short_description = 'Pasajero'
    
    def get_vuelo(self, obj):
        """Mostrar información del vuelo"""
        vuelo = obj.reserva.vuelo
        return f"{vuelo.origen} → {vuelo.destino}"
    get_vuelo.short_description = 'Vuelo'
    
    def marcar_usado(self, request, queryset):
        """Acción para marcar boletos como usados"""
        updated = queryset.update(estado='usado')
        self.message_user(
            request, 
            f'{updated} boleto(s) marcado(s) como usado(s)'
        )
    marcar_usado.short_description = "Marcar como usado"
    
    def marcar_perdido(self, request, queryset):
        """Acción para marcar boletos como perdidos"""
        updated = queryset.update(estado='perdido')
        self.message_user(
            request, 
            f'{updated} boleto(s) marcado(s) como perdido(s)'
        )
    marcar_perdido.short_description = "Marcar como perdido"

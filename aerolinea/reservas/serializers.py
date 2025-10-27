"""
Serializers para la aplicación reservas.

Este archivo define los serializers relacionados con:
- Reservas
- Boletos
"""

from rest_framework import serializers
from .models import Reserva, Boleto
from vuelos.serializers import VueloSerializer
from pasajeros.serializers import PasajeroSerializer


class ReservaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Reserva.
    """
    vuelo_detalle = VueloSerializer(source='vuelo', read_only=True)
    pasajero_detalle = PasajeroSerializer(source='pasajero', read_only=True)
    asiento_numero = serializers.CharField(source='asiento.numero', read_only=True)
    asiento_tipo = serializers.CharField(source='asiento.tipo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_confirmada = serializers.BooleanField(read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)
    puede_cancelar = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ('id', 'codigo_reserva', 'fecha_reserva',)
        depth = 2


class ReservaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar reservas.
    """
    ruta_vuelo = serializers.SerializerMethodField()
    pasajero_nombre = serializers.SerializerMethodField()
    asiento_numero = serializers.CharField(source='asiento.numero', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Reserva
        fields = ['id', 'codigo_reserva', 'ruta_vuelo', 'pasajero_nombre',
                  'asiento_numero', 'precio', 'estado', 'estado_display',
                  'fecha_reserva', 'fecha_vencimiento']
    
    def get_ruta_vuelo(self, obj):
        """Retorna la ruta del vuelo."""
        return f"{obj.vuelo.origen} → {obj.vuelo.destino}"
    
    def get_pasajero_nombre(self, obj):
        """Retorna el nombre completo del pasajero."""
        return obj.pasajero.get_nombre_completo()


class BoletoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Boleto.
    """
    reserva_detalle = ReservaListSerializer(source='reserva', read_only=True)
    vuelo_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Boleto
        fields = '__all__'
        read_only_fields = ('id', 'codigo_barra', 'fecha_emision',)
    
    def get_vuelo_info(self, obj):
        """Retorna información del vuelo asociado."""
        return obj.get_informacion_vuelo()


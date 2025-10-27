"""
Serializers para la aplicación vuelos.

Este archivo define los serializers relacionados con:
- Aviones
- Asientos
- Vuelos
"""

from rest_framework import serializers
from .models import Avion, Asiento, Vuelo


class AvionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Avion.
    """
    
    class Meta:
        model = Avion
        fields = '__all__'
        read_only_fields = ('id',)


class AsientoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Asiento.
    """
    avion_modelo = serializers.CharField(source='avion.modelo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Asiento
        fields = '__all__'
        read_only_fields = ('id',)


class VueloSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Vuelo.
    """
    avion_modelo = serializers.CharField(source='avion.modelo', read_only=True)
    avion_capacidad = serializers.IntegerField(source='avion.capacidad', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Vuelo
        fields = '__all__'
        read_only_fields = ('id',)


class VueloListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar vuelos.
    """
    avion_modelo = serializers.CharField(source='avion.modelo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    ruta = serializers.SerializerMethodField()
    
    class Meta:
        model = Vuelo
        fields = ['id', 'origen', 'destino', 'ruta', 'fecha_salida', 
                  'fecha_llegada', 'duracion', 'estado', 'estado_display',
                  'precio_base', 'avion_modelo']
    
    def get_ruta(self, obj):
        """Retorna la ruta del vuelo como string."""
        return f"{obj.origen} → {obj.destino}"

